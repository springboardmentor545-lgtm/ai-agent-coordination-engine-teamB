import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

# Fresh thread_id -- simulating a brand new conversation
thread_config = {"configurable": {"thread_id": "test-thread-new-conversation"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I'd like to request leave from Nov 5 to Nov 6",
    "employee_id": "EMP1005",  # same employee from the previous test, has 1 past APPROVE on record
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Research narrative (check if past decisions are mentioned) ---")
print(result["research"]["narrative"])

print("\n--- Decision ---")
print(result.get("decision"))