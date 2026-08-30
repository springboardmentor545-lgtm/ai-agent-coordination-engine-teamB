from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config.settings import GROQ_API_KEY


class DecisionAgent:

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b"
    ):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.2
        )

    def decide(
        self,
        user_query: str,
        analysis_result: str
    ) -> str:
        """
        Decision Agent provides the final response
        based on the analysis.
        """

        prompt = f"""
You are the Decision Agent in a multi-agent AI system.

Your responsibility is to provide the final answer
to the user based on the analysis from the previous agent.

User request:
{user_query}

Analysis:
{analysis_result}

Give a clear and concise final answer.
Do not mention internal agents or technical processing.
"""

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content