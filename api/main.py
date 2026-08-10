from fastapi import FastAPI
from pydantic import BaseModel
from agents.base_agent import Agent
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

app = FastAPI(title="Enterprise Workflow Platform with Decision Automation System - Milestone 2")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "agent_name": "Planning Agent",
            "response": "Please enter a valid question as text. Make sure the 'question' field is included and is a string."
        }
    )

# Create one instance of our agent when the app starts
planning_agent = Agent(name="Planning Agent")


# Pydantic model defines the shape of the incoming request
class PromptRequest(BaseModel):
    question: str


# Pydantic model defines the shape of the outgoing response
class PromptResponse(BaseModel):
    agent_name: str
    response: str


@app.get("/")
def root():
    return {"message": "AI Agent is running. Visit /docs to test it."}


@app.post("/ask", response_model=PromptResponse)
def ask_agent(request: PromptRequest):
    answer = planning_agent.think(request.question)
    return PromptResponse(agent_name=planning_agent.name, response=answer)