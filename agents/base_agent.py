from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage

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

        # Initialize Groq LLM
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.7
        )

        # Available tools
        self.tools = [
            currency_converter,
            calculator
        ]

        # Allow the LLM to decide when a tool is needed
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Map tool names to actual tools
        self.tool_map = {
            "currency_converter": currency_converter,
            "calculator": calculator
        }

    def think(self, question: str) -> str:
        """
        Takes a user's question and allows the AI agent
        to decide whether a tool is required.
        """

        messages = [
            HumanMessage(content=question)
        ]

        # Ask the LLM to process the question
        response = self.llm_with_tools.invoke(messages)

        # Check whether the LLM selected a tool
        if response.tool_calls:

            messages.append(response)

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the selected tool
                if tool_name in self.tool_map:

                    tool = self.tool_map[tool_name]

                    tool_result = tool.invoke(tool_args)

                    messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        )
                    )

            # Send the tool result back to the LLM
            final_response = self.llm_with_tools.invoke(messages)

            return final_response.content

        # If no tool is required, return the normal LLM response
        return response.content