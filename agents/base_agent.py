from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from config.settings import GROQ_API_KEY
from tools.weather_tool import weather_tool
from tools.calculator_tool import calculator_tool

class Agent:
    def __init__(self, name: str, model: str = "llama-3.3-70b-versatile"):
        self.name = name

        # Initialize the connection to the LLM (Groq in our case)
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.7
        )

        # List of tools this agent is allowed to use
        self.tools = [weather_tool, calculator_tool]

        # Build a tool-calling agent: the LLM decides whether to answer
        # directly or call one of the tools first
        self.agent_executor = create_react_agent(self.llm, self.tools)

    def think(self, question: str) -> str:
       """
       Takes a user's question, lets the agent decide whether it needs
       a tool or can answer directly, and returns the final response.
       """
       system_instruction = (
           "You are a helpful assistant with access to a weather tool. "
           "If the user asks about weather but does not mention a specific city, "
           "ask them to clarify which city they mean instead of guessing one."
       )

       result = self.agent_executor.invoke(
           {"messages": [
               ("system", system_instruction),
               ("user", question)
           ]}
       )

       final_message = result["messages"][-1]
       return final_message.content