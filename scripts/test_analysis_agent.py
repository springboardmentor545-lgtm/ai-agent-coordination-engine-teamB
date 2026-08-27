import sys
sys.path.append(".")

from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent

fake_state = {
    "user_query": "I want to take leave from Sept 10 to Sept 12",
    "employee_id": "EMP1001",
    "plan": "Check leave balance and team calendar for conflicts",
    "completed_steps": [],
    "request_date": "2026-09-05",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
}

state_after_research = research_agent(fake_state)
print("--- Research completed, moving to Analysis ---\n")

state_after_analysis = analysis_agent(state_after_research)

print("--- Analysis Narrative ---")
print(state_after_analysis["analysis"]["narrative"])

print("\n--- Rule Results (structured) ---")
print(state_after_analysis["analysis"]["rule_results"])

print("\n--- Full State Keys ---")
print(list(state_after_analysis.keys()))
print("\n--- Completed Steps ---")
print(state_after_analysis["completed_steps"])