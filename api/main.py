from fastapi import FastAPI
from pydantic import BaseModel
from agents.base_agent import Agent

app = FastAPI(title="AI Agent Coordination & Decision Engine - Milestone 1")

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