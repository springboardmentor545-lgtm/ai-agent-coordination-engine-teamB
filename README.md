# Development of Enterprise Workflow Platform with Decision Automation System
An AI agent built using **LangChain, Groq, and FastAPI**, extended with an external Weather Tool for retrieving real-time weather information.

## Milestone 1 – Agent Foundation

### Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_weather_api_key
```

### Run

```bash
uvicorn api.main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

### Milestone 1 Features

* Basic LangChain Agent using Groq LLM
* FastAPI `POST /ask` endpoint
* Pydantic request/response validation
* Basic error handling

---

## Milestone 2 – Weather Tool Integration

The agent was extended with an external **Weather Tool** using WeatherAPI.

### Workflow

```text
User
 ↓
FastAPI
 ↓
LangChain Agent
 ↓
 ┌──────────────────┬─────────────────┐
 │ Weather-related  │ Other questions │
 ↓                  ↓
Weather Tool        LLM
 ↓
Weather API
 ↓
Final Response
```

The agent can use the Weather Tool when current weather information is required and use the LLM directly for general questions.

### Weather Tool

Implemented in:

```text
tools/weather_tool.py
```

The tool provides:

* Current temperature
* Weather condition
* Humidity
* Wind speed
* City and country

### Validation & Error Handling

The application handles:

* Empty and whitespace-only questions
* Missing or invalid request fields
* Invalid city names
* Missing API keys
* Weather API failures
* API timeouts and connection errors
* Unexpected application errors

Invalid API requests are rejected with appropriate HTTP validation errors before reaching the agent.

### Testing

The implementation was tested locally for:

* Normal LLM questions
* Weather-related questions
* Different cities
* Invalid cities
* Empty/invalid inputs
* API failures
* FastAPI endpoint behavior

### Project Structure

```text
ai-agent-coordination-engine-teamB/
├── agents/
│   └── base_agent.py
├── api/
│   └── main.py
├── tools/
│   └── weather_tool.py
├── test_agent.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

### Technologies

**Python · LangChain · Groq · FastAPI · Pydantic · WeatherAPI · Requests · Git/GitHub**

> **Security:** API keys are stored locally in `.env`. The `.env` file is excluded from Git; only `.env.example` is committed.
