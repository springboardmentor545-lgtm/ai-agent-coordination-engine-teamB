from fastapi import FastAPI
from pydantic import BaseModel, Field
from agents.decision_agent import DecisionAgent
from memory.conversation_store import add_event, get_history

app = FastAPI(title="Enterprise Workflow Platform - Module 2")
agent = DecisionAgent()

class WorkflowRequest(BaseModel):
    request: str = Field(min_length=1)
    session_id: str = Field(default="default", min_length=1)

@app.get("/health")
def health():
    return {"status": "ok", "module": "2"}

@app.post("/workflow/execute")
def execute_workflow(payload: WorkflowRequest):
    result = agent.execute(payload.request)
    add_event(payload.session_id, payload.request, result)
    return result

@app.get("/workflow/history/{session_id}")
def workflow_history(session_id: str):
    return {"session_id": session_id, "events": get_history(session_id)}
