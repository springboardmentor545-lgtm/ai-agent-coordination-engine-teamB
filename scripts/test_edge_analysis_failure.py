import sys
sys.path.append(".")

from unittest.mock import patch
from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-edge-analysis-failure"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

# Deliberately break the Analysis Agent's underlying tool call
with patch("agents.analysis_agent.analysis_worker.think_with_trace", side_effect=Exception("Simulated Analysis Agent crash")):
    result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Completed Steps ---")
print(result["completed_steps"])
print("\n--- Error ---")
print(result.get("error"))
print("\n--- Retry Count ---")
print(result.get("retry_count"))
print("\n--- Decision (if any) ---")
print(result.get("decision"))
print("\n--- Coordinator's Last Decision ---")
print(result.get("coordinator_decision"))