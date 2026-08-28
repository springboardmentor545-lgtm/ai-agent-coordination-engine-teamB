import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-holiday-aware"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Analysis rule_results ---")
print(result["analysis"]["rule_results"])

print("\n--- Decision ---")
print(result.get("decision"))