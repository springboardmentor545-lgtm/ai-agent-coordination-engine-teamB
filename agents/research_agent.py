from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config.settings import GROQ_API_KEY
from tools.currency_converter import currency_converter
from tools.calculator import calculator


class ResearchAgent:

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b"
    ):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.2
        )

        self.tools = [
            currency_converter,
            calculator
        ]

        self.tool_map = {
            "currency_converter": currency_converter,
            "calculator": calculator
        }

        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def research(self, user_query: str, plan: str) -> str:
        """
        Research Agent collects the information required
        to complete the plan using available tools.
        """

        prompt = f"""
You are the Research Agent in a multi-agent AI system.

Your responsibility is to collect the information needed
to complete the plan.

User request:
{user_query}

Plan from the Planning Agent:
{plan}

Use an available tool when the request requires calculation
or currency conversion.

Return the useful research result clearly.
Do not give a final recommendation.
"""

        response = self.llm_with_tools.invoke(
            [HumanMessage(content=prompt)]
        )

        if response.tool_calls:

            tool_results = []

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                if tool_name in self.tool_map:

                    tool = self.tool_map[tool_name]

                    result = tool.invoke(tool_args)

                    tool_results.append(
                        f"{tool_name}: {result}"
                    )

            return "\n".join(tool_results)

        return response.content