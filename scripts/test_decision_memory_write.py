import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph
from db.queries import get_long_term_memory

thread_config = {"configurable": {"thread_id": "test-thread-memory-check"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I want to take leave from Oct 20 to Oct 21",
    "employee_id": "EMP1005",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

result = leave_approval_graph.invoke(initial_state, config=thread_config)
print("Decision:", result.get("decision"))

print("\n--- Long-term memory for EMP1005 after this run ---")
for record in get_long_term_memory("EMP1005"):
    print(record)