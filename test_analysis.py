from agents.analysis_agent import AnalysisAgent

agent = AnalysisAgent()

question = "Convert 100 USD to INR"

research_result = "currency_converter: 100.0 USD = 9542 INR"

result = agent.analyze(question, research_result)

print("\nANALYSIS AGENT OUTPUT:")
print(result)