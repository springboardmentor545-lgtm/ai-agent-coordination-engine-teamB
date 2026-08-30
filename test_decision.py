from agents.decision_agent import DecisionAgent

agent = DecisionAgent()

question = "Convert 100 USD to INR"

analysis_result = """
100 USD is equivalent to 9542 INR based on the research result.
The actual amount may vary depending on the current exchange rate
and transaction fees.
"""

result = agent.decide(question, analysis_result)

print("\nDECISION AGENT OUTPUT:")
print(result)