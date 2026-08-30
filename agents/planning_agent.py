from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config.settings import GROQ_API_KEY


class PlanningAgent:

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b"
    ):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.3
        )

    def plan(self, user_query: str) -> str:
        """
        Understands the user's request and creates a simple plan.
        """

        prompt = f"""
You are the Planning Agent in a multi-agent AI system.

Your responsibility is to understand the user's request
and break it into clear tasks for the other agents.

User request:
{user_query}

Create a short and clear plan.
Do not answer the user's question.
Only provide the tasks that need to be completed.
"""

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content