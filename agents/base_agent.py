from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY


class Agent:
    def __init__(self, name: str, model: str = "llama-3.3-70b-versatile"):
        self.name = name
        # Initialize the connection to the LLM (Groq in our case)
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.7
        )

    def think(self, question: str) -> str:
        """
        Takes a user's question, sends it to the LLM,
        and returns the AI's response as plain text.
        """
        response = self.llm.invoke(question)
        return response.content