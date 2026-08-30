import uuid
from db.queries import get_session, update_session_cancelled_dates, credit_leave_balance, get_holidays_in_range
from agents_logic.policy_rules import compute_cancellation
from db.queries import get_sessions_for_employee
from services.mixed_resolution_service import resolve_mixed_request
from services.extend_service import process_extension
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from db.queries import save_long_term_memory, get_employee_password_hash
from auth.security import verify_password, create_access_token
from auth.dependencies import get_current_employee
from fastapi import Depends
from graph.leave_approval_graph import leave_approval_graph

from graph.leave_approval_graph import leave_approval_graph

app = FastAPI(title="Enterprise Workflow Platform with Decision Automation System - Milestone 3")


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
    user_query: str
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
    employee_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.get("/")
def root():
    return {"message": "Leave Approval multi-agent system is running. Visit /docs to test it."}


@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    stored_hash = get_employee_password_hash(request.employee_id)
    if stored_hash is None:
        return JSONResponse(status_code=401, content={"error": "Invalid employee ID or password."})

    if not verify_password(request.password, stored_hash):
        return JSONResponse(status_code=401, content={"error": "Invalid employee ID or password."})

    token = create_access_token(request.employee_id)
    return LoginResponse(access_token=token)

@app.post("/leave-request", response_model=LeaveResponse)
def submit_leave_request(request: LeaveRequest, employee_id: str = Depends(get_current_employee)):
    thread_id = request.thread_id or str(uuid.uuid4())

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
def list_sessions(employee_id: str):
    sessions = get_sessions_for_employee(employee_id)
    return {"employee_id": employee_id, "sessions": sessions}

@app.post("/sessions/{thread_id}/cancel")
def cancel_leave(thread_id: str, request: CancelRequest):
    session = get_session(thread_id)
    if session is None:
        return {"error": "Session not found."}
    if session["decision_outcome"] != "APPROVE":
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

    return {
        "thread_id": thread_id,
        "cancelled_dates": result["updated_cancelled_dates"],
        "remaining_dates": result["remaining_dates"],
        "working_days_credited": result["working_days_credited"],
        "message": f"Successfully cancelled {request.dates_to_cancel}. {result['working_days_credited']} day(s) credited back to your leave balance.",
    }

@app.post("/sessions/{thread_id}/extend")
def extend_leave(thread_id: str, request: ExtendRequest):
    if request.start_date != request.end_date:
        return {"error": "Extensions are limited to a single day. Please select just one date on the calendar."}
    return process_extension(thread_id, request.start_date)

@app.post("/sessions/{thread_id}/resolve-mixed")
def resolve_mixed(thread_id: str, request: MixedChoiceRequest):
    return resolve_mixed_request(thread_id, request.choice)