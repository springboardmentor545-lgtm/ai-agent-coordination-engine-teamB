from agents.planning_agent import PlanningAgent

agent = PlanningAgent()

question = "Convert 100 USD to INR"

result = agent.plan(question)

print("\nPLANNING AGENT OUTPUT:")
print(result)