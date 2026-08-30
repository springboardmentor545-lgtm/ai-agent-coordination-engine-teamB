from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from uuid import uuid4

from agents.workflow import app_workflow
from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory


app = FastAPI(
    title="Development of Enterprise Workflow Platform with Decision Automation System - Milestone 3"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memory instances
short_term_memory = ShortTermMemory()
long_term_memory = LongTermMemory()


class PromptRequest(BaseModel):
    question: str
    session_id: str | None = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be empty.")

        return value.strip()


class PromptResponse(BaseModel):
    session_id: str
    response: str


@app.get("/")
def root():
    return {
        "message": "Multi-Agent AI system is running. Visit /docs to test it."
    }


@app.post("/ask", response_model=PromptResponse)
def ask_agent(request: PromptRequest):

    # Create or reuse session
    session_id = request.session_id or str(uuid4())

    try:
        # Retrieve previous conversation
        conversation_history = short_term_memory.get_history(session_id)

        # Retrieve persistent memories
        long_term_memories = long_term_memory.get_memories(session_id)

        # Store current user message
        short_term_memory.add_message(
            session_id,
            "user",
            request.question
        )

        # Shared state passed between all agents
        initial_state = {
            "user_query": request.question,
            "session_id": session_id,
            "conversation_history": conversation_history,
            "long_term_memories": long_term_memories
        }

        # Run Planning → Research → Analysis → Decision
        result = app_workflow.invoke(initial_state)

        # Check whether any agent reported an error
        if result.get("error"):
            error_message = result["error"]

            # Store the error in short-term memory
            short_term_memory.add_message(
                session_id,
                "assistant",
                f"Workflow error: {error_message}"
            )

            raise HTTPException(
                status_code=500,
                detail=error_message
            )

        # Validate that the Decision Agent actually produced an answer
        final_answer = result.get("final_decision")

        if not final_answer or not str(final_answer).strip():
            raise HTTPException(
                status_code=500,
                detail="Decision Agent did not produce a final answer."
            )

        final_answer = str(final_answer).strip()

        # Store assistant response in short-term memory
        short_term_memory.add_message(
            session_id,
            "assistant",
            final_answer
        )

        # Store final result in long-term memory
        long_term_memory.save_memory(
            session_id,
            final_answer
        )

        return PromptResponse(
            session_id=session_id,
            response=final_answer
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow error: {str(e)}"
        )