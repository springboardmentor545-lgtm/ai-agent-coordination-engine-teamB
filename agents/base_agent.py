from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config.settings import GROQ_API_KEY
from tools.currency_converter import currency_converter
from tools.calculator import calculator


class Agent:

    def __init__(
        self,
        name: str,
        model: str = "llama-3.3-70b-versatile"
    ):
        self.name = name

        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.7
        )

        self.tools = [
            currency_converter,
            calculator
        ]

        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.tool_map = {
            "currency_converter": currency_converter,
            "calculator": calculator
        }

    def think(self, question: str) -> str:

        messages = [
            HumanMessage(content=question)
        ]

        # Ask the LLM to decide whether a tool is required
        response = self.llm_with_tools.invoke(messages)

        # If the LLM selected a tool
        if response.tool_calls:

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Execute the selected tool
                if tool_name in self.tool_map:

                    tool = self.tool_map[tool_name]

                    tool_result = tool.invoke(tool_args)

                    # Return the actual tool result
                    return str(tool_result)

        # If no tool is required, return normal LLM answer
        return response.content