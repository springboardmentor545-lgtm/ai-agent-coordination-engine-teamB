import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

thread_config = {"configurable": {"thread_id": "diagnose-conflict-001"}, "recursion_limit": 25}

print("--- Call 1: original request ---")
state1 = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result1 = leave_approval_graph.invoke(state1, config=thread_config)
print("start_date:", result1.get("start_date"))
print("end_date:", result1.get("end_date"))
print("decision:", result1.get("decision"))
print("team_calendar raw data:", result1["research"]["raw_data"].get("fetch_team_calendar"))

print("\n\n--- Call 2: follow-up, extend by a day ---")
state2 = {
    "user_query": "Actually, can we extend it by one more day, until Sept 13?",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}
result2 = leave_approval_graph.invoke(state2, config=thread_config)
print("start_date:", result2.get("start_date"))
print("end_date:", result2.get("end_date"))
print("decision:", result2.get("decision"))
print("team_calendar raw data:", result2["research"]["raw_data"].get("fetch_team_calendar"))
print("\n\n--- Full Research raw_data for Call 2 ---")
for tool_name, data in result2["research"]["raw_data"].items():
    print(f"\n{tool_name}: {data}")

print("\n\n--- Research narrative for Call 2 ---")
print(result2["research"]["narrative"])