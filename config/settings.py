import os
from dotenv import load_dotenv

<<<<<<< HEAD
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Enterprise Workflow Platform")
APP_ENV = os.getenv("APP_ENV", "development")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
=======
# Load variables from .env into the environment
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Did you create a .env file?")
>>>>>>> c3947e8381429ac462fd9c02c6675e6969060595
