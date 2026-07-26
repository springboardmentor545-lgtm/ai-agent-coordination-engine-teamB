import os
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Did you create a .env file?")