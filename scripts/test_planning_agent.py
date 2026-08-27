import sys
sys.path.append(".")

from agents.planning_agent import planning_agent
from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent
from agents.decision_agent import decision_agent

fake_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12 for a family function",
    "employee_id": "EMP1001",
    "completed_steps": [],
}

state = planning_agent(fake_state)
print("--- Planning done ---")
print("start_date:", state["start_date"])
print("end_date:", state["end_date"])
print("request_date:", state["request_date"])
print("plan:", state["plan"])
print("fetched_data:", state["fetched_data"])
print()

state = research_agent(state)
print("--- Research done ---")

state = analysis_agent(state)
print("--- Analysis done ---")

state = decision_agent(state)
print("--- Decision done ---\n")

print("--- Final Decision ---")
print(state["decision"])

print("\n--- Completed Steps ---")
print(state["completed_steps"])