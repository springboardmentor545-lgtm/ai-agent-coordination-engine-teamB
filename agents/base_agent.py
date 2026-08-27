from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY


class Agent:
    def __init__(self, name, tools=None, system_instruction="", model="openai/gpt-oss-120b"):
        self.name = name
        self.llm = ChatGroq(api_key=GROQ_API_KEY, model=model, temperature=0.7)
        self.tools = tools or []
        self.system_instruction = system_instruction
        self.agent_executor = create_react_agent(self.llm, self.tools)

    def think(self, task):
        result = self.agent_executor.invoke({"messages": [
            ("system", self.system_instruction),
            ("user", task)
        ]})
        return result["messages"][-1].content

    def think_with_trace(self, task):
        result = self.agent_executor.invoke({"messages": [
            ("system", self.system_instruction),
            ("user", task)
        ]})
        return result