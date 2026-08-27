import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-thread-001"}, "recursion_limit": 25}

print("--- Call 1: Initial request ---")
initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result1 = leave_approval_graph.invoke(initial_state, config=thread_config)
print("Decision:", result1.get("decision"))
print("Completed steps:", result1["completed_steps"])

print("\n--- Checking what LangGraph remembers for this thread ---")
snapshot = leave_approval_graph.get_state(thread_config)
print("Remembered employee_id:", snapshot.values.get("employee_id"))
print("Remembered start_date:", snapshot.values.get("start_date"))
print("Remembered completed_steps:", snapshot.values.get("completed_steps"))

print("\n\n--- Call 2: Follow-up request, same thread ---")
followup_state = {
    "user_query": "Actually, can we extend it by one more day, until Sept 13?",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result2 = leave_approval_graph.invoke(followup_state, config=thread_config)
print("Decision:", result2.get("decision"))
print("Completed steps:", result2["completed_steps"])
print("employee_id used:", result2.get("employee_id"))
print("start_date used:", result2.get("start_date"))
print("end_date used:", result2.get("end_date"))