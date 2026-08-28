import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph
from db.queries import get_leave_balance

thread_config = {"configurable": {"thread_id": "test-deduction-e2e"}, "recursion_limit": 25}

print("--- Balance before ---")
print(get_leave_balance("EMP1005"))

initial_state = {
    "user_query": "I want to take leave from Oct 20 to Oct 21",
    "employee_id": "EMP1005",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result = leave_approval_graph.invoke(initial_state, config=thread_config)
print("\nDecision:", result.get("decision"))

print("\n--- Balance after ---")
print(get_leave_balance("EMP1005"))