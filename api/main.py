from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from agents.base_agent import Agent


app = FastAPI(
    title="AI Agent Coordination & Decision Engine - Milestone 2"
)


# Create one instance of our agent when the app starts
planning_agent = Agent(name="Planning Agent")


# Pydantic model defines the shape and validation
# of the incoming request
class PromptRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be empty.")

        return value.strip()


# Pydantic model defines the shape of the outgoing response
class PromptResponse(BaseModel):
    agent_name: str
    response: str


@app.get("/")
def root():
    return {
        "message": "AI Agent is running. Visit /docs to test it."
    }


@app.post("/ask", response_model=PromptResponse)
def ask_agent(request: PromptRequest):

    try:
        answer = planning_agent.think(request.question)

        return PromptResponse(
            agent_name=planning_agent.name,
            response=answer
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        )