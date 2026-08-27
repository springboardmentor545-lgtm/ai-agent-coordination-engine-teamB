import sys
sys.path.append(".")

from unittest.mock import patch
from graph.leave_approval_graph import leave_approval_graph
import db.queries

thread_config = {"configurable": {"thread_id": "test-edge-db-down"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

def broken_connection():
    raise Exception("Simulated database outage: connection refused")

with patch.object(db.queries, "get_connection", side_effect=broken_connection):
    result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Completed Steps ---")
print(result["completed_steps"])
print("\n--- Error ---")
print(result.get("error"))
print("\n--- Retry Count ---")
print(result.get("retry_count"))
print("\n--- Decision (should be None) ---")
print(result.get("decision"))
print("\n--- Coordinator's Last Decision ---")
print(result.get("coordinator_decision"))