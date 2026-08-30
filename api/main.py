from fastapi import FastAPI
from pydantic import BaseModel

from workflow import app as workflow_app


app = FastAPI(
    title="Development of Enterprise Workflow Platform with Decision Automation System"
)


class PromptRequest(BaseModel):
    question: str


class PromptResponse(BaseModel):
    agent_name: str
    response: str


@app.get("/")
def root():
    return {
        "message": "Multi-Agent AI System is running. Visit /docs to test it."
    }


@app.post("/ask", response_model=PromptResponse)
def ask_agent(request: PromptRequest):

    result = workflow_app.invoke({
        "user_query": request.question
    })

    return PromptResponse(
        agent_name="Multi-Agent System",
        response=result["final_decision"]
    )