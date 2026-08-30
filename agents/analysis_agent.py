from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config.settings import GROQ_API_KEY


class AnalysisAgent:

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b"
    ):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.2
        )

    def analyze(self, user_query: str, research_result: str) -> str:
        """
        Analysis Agent processes the research result
        and produces a clear analysis.
        """

        prompt = f"""
You are the Analysis Agent in a multi-agent AI system.

Your responsibility is to analyze the information
provided by the Research Agent.

User request:
{user_query}

Research result:
{research_result}

Analyze the result and explain what it means.
Do not use external tools.
Do not give a final recommendation.
Keep the analysis clear and concise.
"""

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content