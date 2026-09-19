from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_query: str

    plan: str
    research_result: str
    analysis: str

    validation_status: str
    final_decision: str

    workflow_id: int
    workflow_start_time: float