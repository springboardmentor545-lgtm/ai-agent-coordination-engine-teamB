import sys
sys.path.append(".")

from agents.planning_agent import planning_agent
from agents.research_agent import research_agent

fake_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12",
    "employee_id": "EMP9999",  # does not exist
    "completed_steps": [],
}

state = planning_agent(fake_state)
print("--- Planning done ---")
print("error:", state["error"])

state = research_agent(state)
print("\n--- Research attempted ---")
print("error:", state["error"])
print("completed_steps:", state["completed_steps"])