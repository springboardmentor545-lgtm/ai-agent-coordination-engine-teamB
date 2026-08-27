import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-edge-no-dates"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I need some time off soon, not sure exactly when yet",
    "employee_id": "EMP1002",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Completed Steps ---")
print(result["completed_steps"])
print("\n--- start_date / end_date ---")
print(result.get("start_date"), "/", result.get("end_date"))
print("\n--- Error ---")
print(result.get("error"))
print("\n--- Decision (if any) ---")
print(result.get("decision"))
print("\n--- Coordinator's Last Decision ---")
print(result.get("coordinator_decision"))