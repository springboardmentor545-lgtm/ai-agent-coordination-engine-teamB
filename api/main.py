import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from graph.leave_approval_graph import leave_approval_graph

app = FastAPI(title="Enterprise Workflow Platform with Decision Automation System - Milestone 3")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid request. Make sure 'employee_id' and 'user_query' are included and are text."
        }
    )


class LeaveRequest(BaseModel):
    employee_id: str
    user_query: str
    thread_id: Optional[str] = None


class LeaveResponse(BaseModel):
    thread_id: str
    decision: Optional[str] = None
    completed_steps: list
    error: Optional[str] = None


@app.get("/")
def root():
    return {"message": "Leave Approval multi-agent system is running. Visit /docs to test it."}


@app.post("/leave-request", response_model=LeaveResponse)
def submit_leave_request(request: LeaveRequest):
    thread_id = request.thread_id or str(uuid.uuid4())

    initial_state = {
        "user_query": request.user_query,
        "employee_id": request.employee_id,
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