# Development of Enterprise Workflow Platform with Decision Automation System

## Project Overview

The **Development of Enterprise Workflow Platform with Decision Automation System** is a multi-agent AI platform designed to automate enterprise workflows and decision-making tasks.

The system accepts a user request, creates a plan, performs research using available tools, analyzes the collected information, validates the workflow state, and generates a final decision.

The workflow is orchestrated using **LangGraph**, while **LangChain and Groq** are used for AI agent capabilities. The system also provides short-term and long-term memory and exposes the workflow through a **FastAPI** REST API.

---

## Objectives

The main objectives of the project are:

- Automate complex workflows using AI agents.
- Divide tasks among specialized agents.
- Coordinate multiple agents using LangGraph.
- Use external tools when required.
- Share information between agents using a common state.
- Analyze research results before making decisions.
- Validate workflow information.
- Maintain short-term and long-term memory.
- Handle errors gracefully.
- Provide the complete workflow through a REST API.

---

## System Architecture

The system follows a sequential multi-agent architecture.

```text
                    User Request
                         |
                         v
                +----------------+
                | Planning Agent |
                +----------------+
                         |
                         v
                +----------------+
                | Research Agent |
                |  + Tools       |
                +----------------+
                         |
                         v
                +----------------+
                | Analysis Agent |
                +----------------+
                         |
                         v
                +----------------+
                |   Validation   |
                +----------------+
                         |
                         v
                +----------------+
                | Decision Agent |
                +----------------+
                         |
                         v
                +----------------+
                |     Memory     |
                | Short + Long   |
                +----------------+
                         |
                         v
                  Final Decision
                         |
                         v
                    FastAPI API
```

---

# Multi-Agent Workflow

The workflow is implemented using LangGraph.

```text
START
  |
  v
Planning Agent
  |
  v
Research Agent
  |
  v
Analysis Agent
  |
  v
Validation
  |
  v
Decision Agent
  |
  v
END
```

Each stage receives information from the previous stage through the shared `AgentState`.

---

# Agents

## 1. Planning Agent

The Planning Agent understands the user's request and creates a sequence of tasks required to solve the problem.

### Example

User request:

```text
Convert 100 USD to INR
```

The Planning Agent can create a plan such as:

```text
1. Retrieve the current USD to INR exchange rate.
2. Validate the retrieved data.
3. Calculate the INR amount.
4. Format the result.
5. Return the result.
```

The Planning Agent does not directly provide the final answer. It creates the plan for the remaining agents.

---

## 2. Research Agent

The Research Agent performs the research required by the plan.

The Research Agent can use available tools to obtain information.

For currency conversion, the currency conversion tool is used.

### Example

```text
currency_converter:
100.0 USD = 9539 INR
```

The Research Agent passes this information to the Analysis Agent.

---

## 3. Analysis Agent

The Analysis Agent interprets the information received from the Research Agent.

For example:

```text
Research Result:
100 USD = 9539 INR
```

The Analysis Agent can determine:

```text
100 USD × 95.39 INR/USD = 9539 INR
```

It also provides context about the result, such as the fact that exchange rates can change over time.

---

## 4. Validation

The validation component checks whether the required information is available before the final decision is generated.

The validation checks:

- User query
- Planning result
- Research result
- Analysis result

If required information is missing, an error message can be generated.

---

## 5. Decision Agent

The Decision Agent uses the analysis result to generate the final response.

### Example

```text
100 USD is approximately 9,539 INR.
```

The Decision Agent provides the final user-facing decision.

---

# Shared State

The agents communicate using a shared state defined using Python `TypedDict`.

```python
from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_query: str
    plan: str
    research_result: str
    analysis: str
    final_decision: str
```

The state allows information to flow through the workflow.

### State Flow

```text
user_query
     |
     v
plan
     |
     v
research_result
     |
     v
analysis
     |
     v
final_decision
```

---

# LangGraph Workflow

LangGraph is used to coordinate the different agents.

The workflow contains the following nodes:

```text
planning
research
analysis
validation
decision
```

The workflow edges are:

```text
START → planning
planning → research
research → analysis
analysis → validation
validation → decision
decision → END
```

The workflow is compiled using:

```python
app = graph.compile()
```

---

# Tool Integration

The system supports tool integration through the Research Agent.

## Currency Converter

The currency converter is used for currency-related requests.

### Example request

```text
Convert 100 USD to INR
```

### Tool result

```text
currency_converter: 100.0 USD = 9539 INR
```

The research result is then passed to the Analysis Agent.

---

# Memory System

The project includes two types of memory.

## Short-Term Memory

Short-term memory stores recent user requests and responses.

### Example

```text
User Query:
Convert 100 USD to INR

Response:
100 USD is approximately 9,539 INR.
```

Short-term memory can be used to provide context from recent interactions.

---

## Long-Term Memory

Long-term memory stores important information that should persist between interactions.

### Example

```text
User Query:
What is my project?

Response:
Development of Enterprise Workflow Platform with Decision Automation System
```

The memory is stored in:

```text
memory/memory.json
```

---

# Memory and Error Handling

Successful and meaningful results can be stored in memory.

Failed conversion results are not stored as successful results.

For example:

```text
Convert 100 ABC to INR
```

If the currency conversion service cannot process the request, the system returns a user-friendly error response instead of crashing.

Example:

```text
I’m sorry, but I’m unable to convert 100 ABC to INR right now because the currency conversion service is unavailable.
```

---

# Error Handling

The system is designed to handle errors gracefully.

- Missing user query.
- Missing planning result.
- Missing research result.
- Missing analysis result.
- Invalid currency requests.
- Currency conversion service failure.
- Missing or invalid workflow information.

The objective is to prevent the complete application from failing when an individual operation cannot be completed.

---

# FastAPI Integration

FastAPI is used to expose the multi-agent workflow as a REST API.

The API provides an `/ask` endpoint that accepts a user question.

## Start the API

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Then start the FastAPI server:

```powershell
uvicorn api.main:app --reload
```

The server runs at:

```text
http://127.0.0.1:8000
```

---

# Swagger API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface can be used to test the API.

---

# API Endpoint

## POST `/ask`

The `/ask` endpoint accepts a user question.

### Request

```json
{
    "question": "Convert 100 USD to INR"
}
```

### Response

```json
{
    "agent_name": "Multi-Agent System",
    "response": "$100 USD is approximately ₹9,539.00 INR."
}
```

### HTTP Status

```text
200 OK
```

---

# API Error Example

For an unsupported or unavailable currency conversion request:

### Request

```json
{
    "question": "Convert 100 ABC to INR"
}
```

### Example response

```json
{
    "agent_name": "Multi-Agent System",
    "response": "I’m sorry, but I’m unable to convert 100 ABC to INR right now because the currency conversion service is unavailable."
}
```

The API remains available instead of crashing.

---

# Technologies Used

## Programming Language

- Python

## AI and Agent Frameworks

- LangChain
- LangGraph
- Groq

## API Framework

- FastAPI

## Data Validation

- Pydantic

## Environment Configuration

- Python-dotenv

## Other Technologies

- REST API
- AI Agents
- Tool Integration
- Shared State
- Short-Term Memory
- Long-Term Memory

---

# Project Structure

```text
ai-agent-coordination-engine-teamB/
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── planning_agent.py
│   ├── research_agent.py
│   ├── analysis_agent.py
│   ├── decision_agent.py
│   └── validation.py
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── memory/
│   ├── __init__.py
│   ├── state.py
│   ├── short_term_memory.py
│   ├── long_term_memory.py
│   └── memory.json
│
├── tools/
│   ├── __init__.py
│   └── currency_converter.py
│
├── workflow.py
│
├── test_planning.py
├── test_research.py
├── test_analysis.py
├── test_long_term_memory.py
├── test_workflow.py
│
├── requirements.txt
├── README.md
└── .env
```

---

# Testing

The project has been tested at different stages.

## Planning Agent Test

Run:

```powershell
python test_planning.py
```

This verifies that the Planning Agent can generate a plan.

---

## Research Agent Test

Run:

```powershell
python test_research.py
```

This verifies that the Research Agent can obtain information using the required tool.

Example:

```text
RESEARCH AGENT OUTPUT:
currency_converter: 100.0 USD = 9539 INR
```

---

## Analysis Agent Test

Run:

```powershell
python test_analysis.py
```

This verifies that the Analysis Agent can interpret the research result.

---

## Long-Term Memory Test

Run:

```powershell
python test_long_term_memory.py
```

This verifies long-term memory functionality.

---

## Complete Workflow Test

Run:

```powershell
python test_workflow.py
```

The complete workflow produces:

```text
========== FINAL WORKFLOW RESULT ==========

PLAN:
...

RESEARCH:
...

ANALYSIS:
...

FINAL DECISION:
100 USD ≈ 9,539 INR.
```

---

# End-to-End Workflow Example

## User Request

```text
Convert 100 USD to INR
```

## Planning Agent

```text
Retrieve the exchange rate.
Validate the data.
Calculate the conversion.
Format the result.
Return the result.
```

## Research Agent

```text
currency_converter:
100.0 USD = 9539 INR
```

## Analysis Agent

```text
The exchange rate is approximately 95.39 INR per USD.

100 USD × 95.39 INR/USD = 9539 INR.
```

## Validation

```text
Validation successful.
```

## Decision Agent

```text
100 USD ≈ 9,539 INR.
```

## Final API Response

```json
{
    "agent_name": "Multi-Agent System",
    "response": "$100 USD is approximately ₹9,539.00 INR."
}
```

---

# Key Features

- Multi-agent AI architecture
- Specialized AI agents
- Planning and task decomposition
- Research and tool integration
- Analysis of research results
- Automated decision generation
- LangGraph workflow orchestration
- Shared state management
- Workflow validation
- Error handling
- Short-term memory
- Long-term memory
- FastAPI REST API
- Interactive Swagger documentation
- End-to-end workflow testing

---

# Benefits

The platform provides several benefits:

- Reduces manual workflow processing.
- Divides complex tasks into smaller specialized tasks.
- Enables AI agents to collaborate.
- Improves workflow organization.
- Supports reusable tools.
- Maintains useful information through memory.
- Provides structured decision-making.
- Supports API-based integration.
- Handles errors without stopping the complete system.

---

# Future Scope

The platform can be extended with:

- More specialized AI agents.
- Additional enterprise tools.
- Database-based persistent memory.
- Authentication and authorization.
- Role-based access control.
- Human-in-the-loop approval.
- Parallel agent execution.
- Advanced decision rules.
- Workflow monitoring and logging.
- Enterprise dashboards.
- Integration with external enterprise applications.
- More sophisticated validation and fallback mechanisms.

---

# Conclusion

The **Development of Enterprise Workflow Platform with Decision Automation System** demonstrates how multiple AI agents can collaborate to automate a complete workflow.

The system combines:

```text
AI Agents
+
LangGraph
+
Tool Integration
+
Shared State
+
Validation
+
Memory
+
FastAPI
```

The completed workflow can accept a user request, plan the required tasks, perform research, analyze the results, validate the workflow, make a decision, and return the final result through an API.

This architecture provides a foundation for developing scalable AI-powered enterprise workflow and decision automation systems.