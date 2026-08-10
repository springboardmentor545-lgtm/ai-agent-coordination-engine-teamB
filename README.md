# Development of Enterprise Workflow Platform with Decision Automation System

## Milestone 1 - Agent Foundation Development

### Setup
1. Clone the repository and switch to this branch
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your own Groq API key:
   - Get a free key at https://console.groq.com -> API Keys
   - Create a `.env` file with: `GROQ_API_KEY=your_actual_key_here`

### Run
uvicorn api.main:app --reload

Visit `http://127.0.0.1:8000/docs` to test.

### What's built
- Basic `Agent` class (`agents/base_agent.py`) wrapping a LangChain-Groq LLM connection
- FastAPI endpoint `POST /ask` that accepts a question and returns the agent's response
- Pydantic request/response models for validation

### Testing
Tested via Swagger UI with multiple cases: normal questions, short/vague input, empty strings, long multi-part questions, missing fields, and wrong data types. Invalid input (missing/wrong-type fields) is correctly rejected with 422 errors before reaching the LLM.

## Milestone 2 – Tool Integration & Intelligent Action Execution

### What's new
- Agent upgraded from a plain LLM wrapper to a **tool-calling agent** using LangGraph's `create_react_agent`
- The agent itself decides whether a question needs a tool or can be answered directly from the LLM's own knowledge — this decision is not hardcoded
- **Weather tool** (`tools/weather_tool.py`) — fetches live weather for a city using the free Open-Meteo API (geocoding + current weather, no API key required)
- **Calculator tool** (`tools/calculator_tool.py`) — safely evaluates basic math expressions, with character validation to prevent unsafe input reaching Python's `eval()`
- Both tools built and tested standalone before being wired into the agent

### Tool-calling behavior (tested)
- Weather questions with a valid city → tool is called, live data returned
- Weather questions with an invalid/unrecognized city → tool returns a graceful error, LLM relays it naturally instead of crashing
- Weather questions with no city mentioned → agent asks for clarification instead of guessing a city (fixed via a system instruction after initial testing revealed this gap)
- Math questions → calculator tool is called, correct result returned
- General knowledge questions → answered directly by the LLM, no tool called
- Verified via message-trace logging that the LLM's tool-call decision (empty content + `tool_calls` populated) is genuinely happening, not just guessed from the final answer

### Validation & error handling
- FastAPI/Pydantic still rejects malformed requests (missing `question` field, wrong data type) before the agent or LLM is ever called
- Added a custom exception handler so invalid requests return a clear, friendly message instead of raw technical validation errors, while still returning proper `422` status codes
- Weather tool handles: city not found, network timeouts, unexpected API responses
- Calculator tool handles: division by zero, invalid expressions, and blocks unsafe characters before evaluation

### Known limitation
- Ambiguous city names (e.g., "Bangalore") can occasionally resolve to an unexpected location via the geocoding API (e.g., a same-named town in another country). The agent has been observed self-correcting using conversational context, but this isn't guaranteed for every ambiguous name.