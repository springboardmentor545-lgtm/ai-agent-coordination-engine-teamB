# ai-agent-coordination-engine-teamB



\# AI Agent Coordination \& Decision Engine



\## Milestone 1 – Agent Foundation Development



\### Setup

1\. Create virtual environment: `python -m venv venv`

2\. Activate: `venv\\Scripts\\activate`

3\. Install dependencies: `pip install -r requirements.txt`

4\. Create a `.env` file with your `GROQ\_API\_KEY`



\### Run
```
uvicorn api.main:app --reload
```


Visit `http://127.0.0.1:8000/docs` to test.



\### What's built

\- Basic `Agent` class (`agents/base\_agent.py`) wrapping a LangChain-Groq LLM connection

\- FastAPI endpoint `POST /ask` that accepts a question and returns the agent's response

\- Pydantic request/response models for validation



\### Testing

Tested via Swagger UI with multiple cases: normal questions, short/vague input, empty strings, long multi-part questions, missing fields, and wrong data types. Invalid input (missing/wrong-type fields) is correctly rejected with 422 errors before reaching the LLM.

