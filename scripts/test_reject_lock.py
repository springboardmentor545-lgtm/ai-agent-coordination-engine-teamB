import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-reject-lock-2"}, "recursion_limit": 25}

print("--- Call 1: EMP1004 (balance 2), requesting Oct 6-8 (3 weekdays, no holidays), expect REJECT ---")
state1 = {
    "user_query": "I want to take leave from Oct 6 to Oct 8",
    "employee_id": "EMP1004",
    "thread_id": "test-reject-lock-2",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result1 = leave_approval_graph.invoke(state1, config=thread_config)
print("decision_outcome:", result1.get("decision_outcome"))
print("decision:", result1.get("decision"))

print("\n--- Call 2: trying to modify after rejection, should be LOCKED ---")
state2 = {
    "user_query": "Can I just take 1 day instead?",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result2 = leave_approval_graph.invoke(state2, config=thread_config)
print("completed_steps:", result2["completed_steps"])
print("decision:", result2.get("decision"))