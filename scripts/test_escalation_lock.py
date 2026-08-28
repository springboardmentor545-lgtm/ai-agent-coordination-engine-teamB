import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-escalation-lock"}, "recursion_limit": 25}

print("--- Call 1: original request, expect ESCALATE ---")
state1 = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result1 = leave_approval_graph.invoke(state1, config=thread_config)
print("decision_outcome:", result1.get("decision_outcome"))
print("decision:", result1.get("decision"))

print("\n\n--- Call 2: trying to extend after escalation, should be LOCKED ---")
state2 = {
    "user_query": "Actually, can we extend it by one more day, until Sept 13?",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result2 = leave_approval_graph.invoke(state2, config=thread_config)
print("completed_steps:", result2["completed_steps"])
print("decision:", result2.get("decision"))