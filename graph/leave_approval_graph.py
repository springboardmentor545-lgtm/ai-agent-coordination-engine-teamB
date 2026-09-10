from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
import os

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
    decision_outcome: Optional[str]
    error: Optional[str]
    retry_count: dict
    coordinator_decision: dict
    final_response: str
    delta_applied: bool
    delta_note: str
    mixed_choice_pending: bool
    mixed_split_info: dict


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

DATABASE_URL = os.getenv("DATABASE_URL")

# A single long-lived Connection (the old approach) gets silently closed by
# Neon after a period of idleness, causing "connection is closed" errors on
# the next graph call. A ConnectionPool is self-healing: it discards dead
# connections and opens fresh ones automatically, and PostgresSaver accepts
# a pool in place of a single connection natively (no workaround needed).
checkpoint_pool = ConnectionPool(
    conninfo=DATABASE_URL,
    max_size=10,
    kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
    check=ConnectionPool.check_connection,  # validate a connection is alive before handing it out
    max_lifetime=20 * 60,                   # recycle connections every 20 min, before Neon can kill them
    max_idle=5 * 60,                        # also recycle if idle for 5 min
)
checkpointer = PostgresSaver(checkpoint_pool)
checkpointer.setup()

leave_approval_graph = builder.compile(checkpointer=checkpointer)