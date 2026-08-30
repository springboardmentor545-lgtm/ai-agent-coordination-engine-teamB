from agents.research_agent import ResearchAgent

agent = ResearchAgent()

question = "Convert 100 USD to INR"

plan = """
1. Get the current USD to INR exchange rate.
2. Calculate the converted amount.
3. Return the conversion result.
"""

result = agent.research(question, plan)

print("\nRESEARCH AGENT OUTPUT:")
print(result)