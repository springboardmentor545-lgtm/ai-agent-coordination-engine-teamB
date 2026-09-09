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
from auth.security import verify_password, create_access_token
from auth.dependencies import get_current_employee
from fastapi import Depends
from graph.leave_approval_graph import leave_approval_graph
from fastapi.staticfiles import StaticFiles
from auth.security import decode_access_token

app = FastAPI(title="Enterprise Workflow Platform with Decision Automation System - Milestone 3")

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    """
    Logs every HTTP request/response cycle - method, path, status code, and
    true wall-clock duration (including auth, validation, everything) - for
    the Monitoring page's API-level stats. Runs for every endpoint automatically,
    no per-endpoint code needed.
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
def login(request: LoginRequest):
    employee = get_employee_by_email(request.email)
    if employee is None:
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})

    if not verify_password(request.password, employee["password_hash"]):
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})

    token = create_access_token(employee["employee_id"])
    return LoginResponse(access_token=token)

    if not verify_password(request.password, stored_hash):
        return JSONResponse(status_code=401, content={"error": "Invalid employee ID or password."})

    token = create_access_token(request.employee_id)
    return LoginResponse(access_token=token)

@app.post("/leave-request", response_model=LeaveResponse)
def submit_leave_request(request: LeaveRequest, employee_id: str = Depends(get_current_employee)):
    thread_id = request.thread_id or str(uuid.uuid4())

    structured_mode = request.start_date is not None and request.end_date is not None

    if not structured_mode and not request.user_query:
        return JSONResponse(
            status_code=422,
            content={"error": "Provide either start_date and end_date, or a free-text user_query."}
        )

    if structured_mode:
        reason = request.reason or "not specified"
        initial_state = {
            "user_query": f"Leave request from {request.start_date} to {request.end_date}. Reason: {reason}.",
            "structured_request": True,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "fetched_data": {"reason": reason},
            "employee_id": employee_id,
            "thread_id": thread_id,
            "completed_steps": [],
            "retry_count": {},
            "error": None,
        }
    else:
        initial_state = {
            "user_query": request.user_query,
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
def list_sessions(employee_id: str = Depends(get_current_employee)):
    sessions = get_sessions_for_employee(employee_id)
    return {"employee_id": employee_id, "sessions": sessions}

@app.get("/holidays")
def list_holidays(start_date: str, end_date: str, employee_id: str = Depends(get_current_employee)):
    holidays = get_holidays_in_range(start_date, end_date)
    return {"holidays": holidays}


@app.get("/my-leave-dates")
def my_leave_dates(start_date: str, end_date: str, employee_id: str = Depends(get_current_employee)):
    sessions = get_sessions_for_employee(employee_id)
    reserved = get_own_reserved_dates(sessions, start_date, end_date)
    return {"reserved_dates": reserved}

@app.post("/sessions/{thread_id}/cancel")
def cancel_leave(thread_id: str, request: CancelRequest, employee_id: str = Depends(get_current_employee)):
    start_time = time.time()
    session = get_session(thread_id)
    if session is None:
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail="session not found")
        return {"error": "Session not found."}
    if session["employee_id"] != employee_id:
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail="ownership check failed")
        return JSONResponse(status_code=403, content={"error": "You do not have permission to modify this session."})
    if session["decision_outcome"] != "APPROVE":
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail="session is not an approved leave")
        return {"error": "Only approved leave sessions can be cancelled."}

    holidays = set(get_holidays_in_range(session["start_date"], session["end_date"]))

    result = compute_cancellation(
        session["start_date"],
        session["end_date"],
        session["cancelled_dates"],
        request.dates_to_cancel,
        holidays,
    )

    if not result["valid"]:
        log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
                   action="cancel_denied", status="failure", detail=result["error"])
        return {"error": result["error"]}

    update_session_cancelled_dates(thread_id, result["updated_cancelled_dates"])
    if result["working_days_credited"] > 0:
        credit_leave_balance(session["employee_id"], result["working_days_credited"])

    save_long_term_memory(session["employee_id"], "leave_decision", {
        "decision": "APPROVE",
        "start_date": session["start_date"],
        "end_date": session["end_date"],
        "summary": f"Partially cancelled: {request.dates_to_cancel} removed. Remaining active dates: {result['remaining_dates']}.",
    })

    log_event(thread_id=thread_id, employee_id=employee_id, agent_name="Cancel Service",
               action="leave_cancelled", duration_ms=int((time.time() - start_time) * 1000),
               detail=f"cancelled {request.dates_to_cancel}, {result['working_days_credited']} day(s) credited")

    return {
        "thread_id": thread_id,
        "cancelled_dates": result["updated_cancelled_dates"],
        "remaining_dates": result["remaining_dates"],
        "working_days_credited": result["working_days_credited"],
        "message": f"Successfully cancelled {request.dates_to_cancel}. {result['working_days_credited']} day(s) credited back to your leave balance.",
    }

@app.post("/sessions/{thread_id}/extend")
def extend_leave(thread_id: str, request: ExtendRequest, employee_id: str = Depends(get_current_employee)):
    if request.start_date != request.end_date:
        return {"error": "Extensions are limited to a single day. Please select just one date on the calendar."}
    result = process_extension(thread_id, request.start_date, employee_id)
    if result.get("error") == "You do not have permission to modify this session.":
        return JSONResponse(status_code=403, content=result)
    return result

@app.post("/sessions/{thread_id}/resolve-mixed")
def resolve_mixed(thread_id: str, request: MixedChoiceRequest, employee_id: str = Depends(get_current_employee)):
    result = resolve_mixed_request(thread_id, request.choice, employee_id)
    if result.get("error") == "You do not have permission to modify this session.":
        return JSONResponse(status_code=403, content=result)
    return result

@app.get("/sessions/{thread_id}/audit-logs")
def get_session_audit_logs(thread_id: str, employee_id: str = Depends(get_current_employee)):
    session = get_session(thread_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found."})
    if session["employee_id"] != employee_id:
        return JSONResponse(status_code=403, content={"error": "You do not have permission to view this session's logs."})

    # Mixed-conflict split sessions ("{thread}-approved" / "{thread}-escalated") don't have
    # their own audit trail — all agent/tool activity was logged under the original thread_id
    # before the split happened. Strip the suffix so the logs still resolve correctly.
    logs_thread_id = thread_id
    for suffix in ("-approved", "-escalated"):
        if logs_thread_id.endswith(suffix):
            logs_thread_id = logs_thread_id[: -len(suffix)]
            break

    logs = get_audit_logs_for_thread(logs_thread_id)
    return {"thread_id": thread_id, "logs": logs}


@app.get("/monitoring-stats")
def monitoring_stats(employee_id: str = Depends(get_current_employee)):
    return get_monitoring_stats()