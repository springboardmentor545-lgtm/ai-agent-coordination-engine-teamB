import sys
sys.path.append(".")

from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent
from agents.decision_agent import decision_agent

fake_state = {
    "user_query": "I want to take leave from Oct 1 to Oct 5",
    "employee_id": "EMP1004",
    "plan": "Check leave balance and team calendar for conflicts",
    "completed_steps": [],
    "request_date": "2026-09-01",
    "start_date": "2026-10-01",
    "end_date": "2026-10-05",
}

state = research_agent(fake_state)
print("--- Research done ---")
state = analysis_agent(state)
print("--- Analysis done ---")
state = decision_agent(state)
print("--- Decision done ---\n")

print("--- Final Decision ---")
print(state["decision"])

print("\n--- Completed Steps ---")
print(state["completed_steps"])