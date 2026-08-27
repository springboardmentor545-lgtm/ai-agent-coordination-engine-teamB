import sys
sys.path.append(".")

from unittest.mock import patch
from graph.leave_approval_graph import leave_approval_graph
from agents.research_agent import research_worker

thread_config = {"configurable": {"thread_id": "test-edge-successful-retry-2"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

call_count = {"n": 0}
real_think_with_trace = research_worker.think_with_trace

def flaky_think_with_trace(task):
    call_count["n"] += 1
    if call_count["n"] == 1:
        raise Exception("Simulated transient network timeout")
    return real_think_with_trace(task)

with patch.object(research_worker, "think_with_trace", side_effect=flaky_think_with_trace):
    result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Completed Steps ---")
print(result["completed_steps"])
print("\n--- Retry Count ---")
print(result.get("retry_count"))
print("\n--- Final Error (should be None if recovery worked) ---")
print(result.get("error"))
print("\n--- Decision ---")
print(result.get("decision"))
print("\n--- Research's internal LLM call was attempted this many times ---")
print(call_count["n"])