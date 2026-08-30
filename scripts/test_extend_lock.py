import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph
from services.extend_service import process_extension
from db.queries import get_session

thread_config = {"configurable": {"thread_id": "test-extend-lock"}, "recursion_limit": 25}

print("--- Step 1: EMP1004 (balance 2), approve Sept 15-16 ---")
initial_state = {
    "user_query": "I want to take leave from Sept 15 to Sept 16",
    "employee_id": "EMP1004",
    "thread_id": "test-extend-lock",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result = leave_approval_graph.invoke(initial_state, config=thread_config)
print("decision_outcome:", result.get("decision_outcome"))
print(get_session("test-extend-lock"))

print("\n--- Step 2: try to extend to Sept 17 (should REJECT, balance now 0) ---")
extend_result = process_extension("test-extend-lock", "2026-09-17")
print(extend_result)
print(get_session("test-extend-lock"))

print("\n--- Step 3: try to extend AGAIN (should be blocked by extend_locked) ---")
extend_result_2 = process_extension("test-extend-lock", "2026-09-17")
print(extend_result_2)