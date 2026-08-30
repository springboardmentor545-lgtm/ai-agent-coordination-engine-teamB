from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_query: str
    plan: str
    research_result: str
    analysis: str
    final_decision: str