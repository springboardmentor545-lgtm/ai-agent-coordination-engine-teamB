from langchain_groq import ChatGroq

from config.settings import GROQ_API_KEY
from agents.state import AgentState

from tools.weather_tool import get_weather
from tools.calculator_tool import calculator_tool


class ResearchAgent:

    def __init__(self, model: str = "openai/gpt-oss-120b"):
        self.name = "Research Agent"

        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.2
        )

        self.tools = {
            "get_weather": get_weather,
            "calculator_tool": calculator_tool
        }

        self.llm_with_tools = self.llm.bind_tools(
            list(self.tools.values())
        )

    def run(self, state: AgentState) -> AgentState:

        if state.get("error"):
            return state

        query = state["user_query"]
        plan = state.get("plan", [])

        conversation_history = state.get(
            "conversation_history", []
        )

        long_term_memories = state.get(
            "long_term_memories", []
        )

        prompt = f"""
You are the Research Agent in a multi-agent AI system.

Your responsibility is to collect information required to answer
the user's request.

User request:
{query}

Plan:
{plan}

Previous conversation:
{conversation_history}

Relevant long-term memories:
{long_term_memories}

Available tools:

1. get_weather
Use this when the user asks for current weather information.

2. calculator_tool
Use this when the user asks for mathematical calculations.

You MUST use the appropriate tool when the user's request
requires a calculation or current weather information.

Collect the required information and provide concise research results.
"""

        try:

            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = self.llm_with_tools.invoke(messages)

            # Execute requested tools
            if response.tool_calls:

                tool_results = []

                for tool_call in response.tool_calls:

                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    if tool_name not in self.tools:
                        raise ValueError(
                            f"Unknown tool requested: {tool_name}"
                        )

                    tool = self.tools[tool_name]

                    result = tool.invoke(tool_args)

                    tool_results.append(
                        f"{tool_name}: {result}"
                    )

                research_results = "\n".join(tool_results)

            else:
                research_results = response.content

            if not research_results:
                research_results = "No additional research was required."

            return {
                **state,
                "research_results": research_results
            }

        except Exception as e:

            return {
                **state,
                "error": f"Research Agent failed: {str(e)}"
            }