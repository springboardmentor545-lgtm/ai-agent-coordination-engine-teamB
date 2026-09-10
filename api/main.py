import uuid
import time
from observability.audit_logger import log_event
from db.queries import get_session, update_session_cancelled_dates, credit_leave_balance, get_holidays_in_range
from agents_logic.policy_rules import compute_cancellation, get_own_reserved_dates
from db.queries import get_audit_logs_for_thread, get_monitoring_stats
from db.queries import get_sessions_for_employee
from services.mixed_resolution_service import resolve_mixed_request
from services.extend_service import process_extension
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from db.queries import save_long_term_memory, get_employee_password_hash, get_employee_by_email
from auth.security import verify_password, create_access_token, decode_access_token
from auth.dependencies import get_current_employee
from fastapi import Depends
from graph.leave_approval_graph import leave_approval_graph
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


def rate_limit_key(request: Request) -> str:
    """
    Rate-limit key: uses the employee_id from a valid JWT when present, so each
    employee gets their own limit regardless of shared IPs (e.g. office Wi-Fi).
    Falls back to IP address when there's no valid token yet (e.g. /login itself).
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            return decode_access_token(auth_header[len("Bearer "):])
        except Exception:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key)

app = FastAPI(title="Enterprise Workflow Platform with Decision Automation System - Milestone 4")
app.state.limiter = limiter

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")



def _service_response(result: dict):
    """
    Service-layer functions (extend, cancel, mixed-resolution) now include a
    'status_code' key on error dicts, instead of always defaulting to FastAPI's
    implicit 200. This translates that into a real JSONResponse so every
    failure path returns the correct HTTP status - not just the one or two
    that used to be manually special-cased.
    """
    status_code = result.pop("status_code", None)
    if status_code:
        return JSONResponse(status_code=status_code, content=result)
    return result


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please slow down and try again shortly."}
    )


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    """
    Logs every HTTP request/response cycle - method, path, status code, and
    true wall-clock duration (including auth, validation, everything) - for
    the Monitoring page's API-level stats. Runs for every endpoint automatically,
    no per-endpoint code needed. Also captures 429s from rate limiting, since
    this middleware wraps the whole request/response cycle including exception handlers.
    """
    start_time = time.time()

    employee_id = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            employee_id = decode_access_token(auth_header[len("Bearer "):])
        except Exception:
            pass

    response = await call_next(request)

    duration_ms = int((time.time() - start_time) * 1000)
    status = "success" if response.status_code < 400 else "failure"
    request_id = f"http-{uuid.uuid4()}"

    log_event(
        thread_id=request_id, employee_id=employee_id, agent_name="API Gateway",
        action="http_request", status=status, duration_ms=duration_ms,
        http_status=response.status_code, detail=f"{request.method} {request.url.path}"
    )

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    problems = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"] if part != "body")
        problems.append(f"{field} ({err['msg']})")
    detail = "; ".join(problems) if problems else "Request could not be validated."
    return JSONResponse(
        status_code=422,
        content={
            "error": f"Invalid request. Problem with: {detail}"
        }
    )

class LeaveRequest(BaseModel):
    user_query: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    reason: Optional[str] = None
    thread_id: Optional[str] = None

class LeaveResponse(BaseModel):
    thread_id: str
    decision: Optional[str] = None
    completed_steps: list
    error: Optional[str] = None

class CancelRequest(BaseModel):
    dates_to_cancel: list[str]

class ExtendRequest(BaseModel):
    start_date: str
    end_date: str

class MixedChoiceRequest(BaseModel):
    choice: str  # "partial" or "escalate_all"

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.get("/")
def root():
    return {"message": "Leave Approval multi-agent system is running. Visit /docs to test it."}


@app.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest):
    employee = get_employee_by_email(payload.email)
    if employee is None:
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})

    if not verify_password(payload.password, employee["password_hash"]):
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})

    token = create_access_token(employee["employee_id"])
    return LoginResponse(access_token=token)

@app.post("/leave-request", response_model=LeaveResponse)
@limiter.limit("10/minute")
def submit_leave_request(request: Request, payload: LeaveRequest, employee_id: str = Depends(get_current_employee)):
    thread_id = payload.thread_id or str(uuid.uuid4())

    structured_mode = payload.start_date is not None and payload.end_date is not None

    if not structured_mode and not payload.user_query:
        return JSONResponse(
            status_code=422,
            content={"error": "Provide either start_date and end_date, or a free-text user_query."}
        )

    if structured_mode:
        reason = payload.reason or "not specified"
        initial_state = {
            "user_query": f"Leave request from {payload.start_date} to {payload.end_date}. Reason: {reason}.",
            "structured_request": True,
            "start_date": payload.start_date,
            "end_date": payload.end_date,
            "fetched_data": {"reason": reason},
            "employee_id": employee_id,
            "thread_id": thread_id,
            "completed_steps": [],
            "retry_count": {},
            "error": None,
        }
    else:
        initial_state = {
            "user_query": payload.user_query,
            "employee_id": employee_id,
            "thread_id": thread_id,
            "completed_steps": [],
            "retry_count": {},
            "error": None,
        }

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}

    try:
        result = leave_approval_graph.invoke(initial_state, config=config)
    except Exception as e:
        return LeaveResponse(
            thread_id=thread_id,
            decision=None,
            completed_steps=[],
            error=f"Unexpected system error: {str(e)}",
        )

    return LeaveResponse(
        thread_id=thread_id,
        decision=result.get("decision"),
        completed_steps=result.get("completed_steps", []),
        error=result.get("error"),
    )

@app.get("/sessions")
@limiter.limit("60/minute")
def list_sessions(request: Request, employee_id: str = Depends(get_current_employee)):
    sessions = get_sessions_for_employee(employee_id)
    return {"employee_id": employee_id, "sessions": sessions}

@app.get("/holidays")
@limiter.limit("60/minute")
def list_holidays(request: Request, start_date: str, end_date: str, employee_id: str = Depends(get_current_employee)):
    holidays = get_holidays_in_range(start_date, end_date)
    return {"holidays": holidays}


@app.get("/my-leave-dates")
@limiter.limit("60/minute")
def my_leave_dates(request: Request, start_date: str, end_date: str, employee_id: str = Depends(get_current_employee)):
    sessions = get_sessions_for_employee(employee_id)
    reserved = get_own_reserved_dates(sessions, start_date, end_date)
    return {"reserved_dates": reserved}

@app.post("/sessions/{thread_id}/cancel")
@limiter.limit("60/minute")
def cancel_leave(thread_id: str, request: Request, payload: CancelRequest, employee_id: str = Depends(get_current_employee)):
    start_time = time.time()
    session = get_session(thread_id)
    if session is None:
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail="session not found")
        return _service_response({"error": "Session not found.", "status_code": 404})
    if session["employee_id"] != employee_id:
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail="ownership check failed")
        return _service_response({"error": "You do not have permission to modify this session.", "status_code": 403})
    if session["decision_outcome"] != "APPROVE":
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail="session is not an approved leave")
        return _service_response({"error": "Only approved leave sessions can be cancelled.", "status_code": 400})

    holidays = set(get_holidays_in_range(session["start_date"], session["end_date"]))

    result = compute_cancellation(
        session["start_date"],
        session["end_date"],
        session["cancelled_dates"],
        payload.dates_to_cancel,
        holidays,
    )

    if not result["valid"]:
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail=result["error"])
        return _service_response({"error": result["error"], "status_code": 400})

    update_session_cancelled_dates(thread_id, result["updated_cancelled_dates"])
    if result["working_days_credited"] > 0:
        credit_leave_balance(session["employee_id"], result["working_days_credited"])

    save_long_term_memory(session["employee_id"], "leave_decision", {
        "decision": "APPROVE",
        "start_date": session["start_date"],
        "end_date": session["end_date"],
        "summary": f"Partially cancelled: {payload.dates_to_cancel} removed. Remaining active dates: {result['remaining_dates']}.",
    })

    log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
               action="leave_cancelled", duration_ms=int((time.time() - start_time) * 1000),
               detail=f"cancelled {payload.dates_to_cancel}, {result['working_days_credited']} day(s) credited")

    return {
        "thread_id": thread_id,
        "cancelled_dates": result["updated_cancelled_dates"],
        "remaining_dates": result["remaining_dates"],
        "working_days_credited": result["working_days_credited"],
        "message": f"Successfully cancelled {payload.dates_to_cancel}. {result['working_days_credited']} day(s) credited back to your leave balance.",
    }

@app.post("/sessions/{thread_id}/extend")
@limiter.limit("10/minute")
def extend_leave(thread_id: str, request: Request, payload: ExtendRequest, employee_id: str = Depends(get_current_employee)):
    if payload.start_date != payload.end_date:
        return _service_response({"error": "Extensions are limited to a single day. Please select just one date on the calendar.", "status_code": 400})
    result = process_extension(thread_id, payload.start_date, employee_id)
    return _service_response(result)

@app.post("/sessions/{thread_id}/resolve-mixed")
@limiter.limit("10/minute")
def resolve_mixed(thread_id: str, request: Request, payload: MixedChoiceRequest, employee_id: str = Depends(get_current_employee)):
    result = resolve_mixed_request(thread_id, payload.choice, employee_id)
    return _service_response(result)

@app.get("/sessions/{thread_id}/audit-logs")
@limiter.limit("60/minute")
def get_session_audit_logs(request: Request, thread_id: str, employee_id: str = Depends(get_current_employee)):
    session = get_session(thread_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found."})
    if session["employee_id"] != employee_id:
        return JSONResponse(status_code=403, content={"error": "You do not have permission to view this session's logs."})

    logs_thread_id = thread_id
    for suffix in ("-approved", "-escalated"):
        if logs_thread_id.endswith(suffix):
            logs_thread_id = logs_thread_id[: -len(suffix)]
            break

    logs = get_audit_logs_for_thread(logs_thread_id)
    return {"thread_id": thread_id, "logs": logs}


@app.get("/monitoring-stats")
@limiter.limit("30/minute")
def monitoring_stats(request: Request, employee_id: str = Depends(get_current_employee)):
    return get_monitoring_stats()