import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph
from db.queries import get_leave_balance

thread_config = {"configurable": {"thread_id": "test-delta-extension"}, "recursion_limit": 25}

print("--- Call 1: original request, EMP1008, Sept 15-17 (should APPROVE, no conflicts) ---")
state1 = {
    "user_query": "I want to take leave from Sept 15 to Sept 17",
    "employee_id": "EMP1008",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result1 = leave_approval_graph.invoke(state1, config=thread_config)
print("decision:", result1.get("decision"))
print("balance after call 1:", get_leave_balance("EMP1008")["leave_balance"])

print("\n\n--- Call 2: extend by one day, until Sept 18 ---")
state2 = {
    "user_query": "Can I extend my leave by one more day, until Sept 18?",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result2 = leave_approval_graph.invoke(state2, config=thread_config)
print("decision:", result2.get("decision"))
print("balance after call 2:", get_leave_balance("EMP1008")["leave_balance"])
print("\n--- Debug: Call 2 analysis rule_results ---")
print(result2["analysis"]["rule_results"])
print("\n--- Debug: Call 2 decision_outcome ---")
print(result2.get("decision_outcome"))