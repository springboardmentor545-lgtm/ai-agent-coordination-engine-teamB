# AI Agent Coordination & Decision Engine

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