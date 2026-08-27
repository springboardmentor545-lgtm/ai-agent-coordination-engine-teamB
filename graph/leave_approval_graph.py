from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.coordinator_agent import coordinator_agent
from agents.planning_agent import planning_agent
from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent
from agents.decision_agent import decision_agent


class LeaveApprovalState(TypedDict, total=False):
    user_query: str
    employee_id: str
    thread_id: str
    plan: list
    completed_steps: list
    fetched_data: dict
    request_date: str
    start_date: str
    end_date: str
    research: dict
    analysis: dict
    decision: str
    error: Optional[str]
    retry_count: dict
    coordinator_decision: dict
    final_response: str


def route_from_coordinator(state):
    decision = state.get("coordinator_decision", {})
    action = decision.get("action")
    next_agent = decision.get("next_agent")

    if action == "finish":
        return END
    if action in ("dispatch_next", "retry") and next_agent in ("planning", "research", "analysis", "decision"):
        return next_agent
    return END


builder = StateGraph(LeaveApprovalState)

builder.add_node("coordinator", coordinator_agent)
builder.add_node("planning", planning_agent)
builder.add_node("research", research_agent)
builder.add_node("analysis", analysis_agent)
builder.add_node("decision", decision_agent)

builder.set_entry_point("coordinator")

builder.add_conditional_edges(
    "coordinator",
    route_from_coordinator,
    {
        "planning": "planning",
        "research": "research",
        "analysis": "analysis",
        "decision": "decision",
        END: END,
    },
)

builder.add_edge("planning", "coordinator")
builder.add_edge("research", "coordinator")
builder.add_edge("analysis", "coordinator")
builder.add_edge("decision", "coordinator")

leave_approval_graph = builder.compile()