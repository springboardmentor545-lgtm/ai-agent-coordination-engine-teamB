import sys
sys.path.append(".")

from agents.research_agent import research_agent

fake_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12",
    "employee_id": "EMP1001",
    "plan": "Check leave balance and team calendar for conflicts",
    "completed_steps": [],
}

result_state = research_agent(fake_state)

print("--- Narrative (for humans/demo) ---")
print(result_state["research"]["narrative"])

print("\n--- Raw Structured Data (for Analysis Agent) ---")
for tool_name, data in result_state["research"]["raw_data"].items():
    print(f"\n{tool_name}:")
    print(data)

print("\n--- Full State Keys ---")
print(list(result_state.keys()))