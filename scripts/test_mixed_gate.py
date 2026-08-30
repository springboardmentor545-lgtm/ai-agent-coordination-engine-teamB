import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "test-mixed-gate"}, "recursion_limit": 25}

# We need real conflicting data -- let's use EMP1001 (Engineering) with a crafted
# scenario. Since we can't easily inject fake team_calendar into the real pipeline,
# let's use the existing Sept 10-12 seed data but request only Sept 10 (conflict)
# alongside a clean day. For a genuine test, we'll rely on next steps once we
# verify this compiles and runs without error first.

initial_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("--- Completed Steps ---")
print(result["completed_steps"])
print("\n--- Mixed choice pending? ---")
print(result.get("mixed_choice_pending"))
print("\n--- Split info ---")
print(result.get("mixed_split_info"))
print("\n--- Final Response ---")
print(result.get("final_response"))