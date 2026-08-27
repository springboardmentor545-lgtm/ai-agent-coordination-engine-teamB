import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

final_state = leave_approval_graph.invoke(initial_state, config={"recursion_limit": 25})

print("--- Completed Steps ---")
print(final_state["completed_steps"])

print("\n--- Final Decision ---")
print(final_state.get("decision"))

print("\n--- Coordinator's Last Decision ---")
print(final_state.get("coordinator_decision"))