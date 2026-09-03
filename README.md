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


## Milestone 3 - Agent Coordination, Memory Management, Authentication & Frontend

### System chosen
Employee Leave Approval System. Chosen because it has a genuine three-way decision outcome (Approve / Reject / Escalate) that exercises real decision automation rather than just information retrieval, and because short-term (follow-up messages) and long-term (cross-conversation history) memory both map onto it naturally.

### What's new
- Converted the single agent from Milestone 2 into a genuine **5-agent multi-agent system**, coordinated by a supervisor pattern rather than a fixed pipeline
- Agents communicate only through a **single shared state** (`LeaveApprovalState`), following a strict read-then-write pattern
- Implemented **short-term memory** (per-conversation) and **long-term memory** (cross-conversation), both backed by Postgres
- Added full **authentication and authorization** (bcrypt + JWT) across every leave-related endpoint
- Built a working **frontend** (login, dashboard, calendar-based new-request page) - Swagger UI is no longer the only way to use the system
- Added **structured (calendar-driven) leave requests** alongside the original free-text path
- Added **double-booking prevention** so an employee can't request dates they already have approved or pending
- Added **weekend/holiday-aware validation** to the extend feature, so a one-day extension can no longer land on a non-working day
- Dashboard now hides/disables extend options that would land on a weekend or holiday, showing the reason on hover, instead of letting the employee click something that would just get rejected

### Architecture: 5 agents, hub-and-spoke orchestration
| Agent | Role | Tools used |
|---|---|---|
| Coordinator | Meta-supervisor - dispatches the next agent, decides retry vs. finish, enforces deterministic safety rules | None (LLM for routing; safety rules are plain Python, not LLM judgment) |
| Planning | Extracts structured dates/reason from free text, or takes them directly from the calendar; fetches the policy document | None (LLM extraction + file read) |
| Research | Gathers all raw facts needed to evaluate a request | Leave balance, leave history, team calendar, department size, past decisions, holidays |
| Analysis | Applies deterministic policy rules to the research data | `evaluate_leave_policy` |
| Decision | Produces the final Approve/Reject/Escalate outcome; on approval, deducts balance and records history | None (pure reasoning over rule results) |

Every worker agent returns control to the Coordinator after finishing - no agent ever routes directly to another agent:

User -> FastAPI -> Coordinator (creates/monitors plan)
|
+---------------+----------------+----------------+
v v v
Planning Agent Research Agent Analysis -> Decision
| | | |
+----------- all return control to Coordinator -------------+
|
Coordinator re-evaluates state after EACH return,
decides the next action, and produces the final response


Implemented as one LangGraph `StateGraph`, with the Coordinator as a conditional-edge router and plain edges from every worker back to `coordinator`.

The deterministic policy engine (`agents_logic/policy_rules.py`) is intentionally plain Python, not an LLM - it handles weekend/holiday-aware day counting, notice period, balance sufficiency, team-conflict ratio (including a per-day breakdown), cancellations, extensions, and mixed-conflict splitting.

### Memory
- **Short-term**: LangGraph's `PostgresSaver` checkpointer, keyed by `thread_id` - a follow-up message in the same conversation reuses prior context (employee ID, dates) without being told again.
- **Long-term**: a dedicated `long_term_memory` Postgres table. The Decision Agent writes a record after every finalized outcome; the Research Agent reads it back at the start of any new conversation, even a brand-new thread.

### Authentication & authorization
- `bcrypt` password hashing, `PyJWT` tokens (8-hour expiry)
- `POST /login` returns a generic error for both "employee not found" and "wrong password", to avoid leaking which employee IDs exist
- Every leave-related endpoint requires a valid JWT; `employee_id` is read only from the verified token, never from the request body or query parameters
- **Ownership checks** on extend/cancel/resolve-mixed prevent one authenticated employee from acting on another employee's session, even if they know its `thread_id` - authentication alone (proving who you are) isn't the same as authorization (proving you're allowed to touch this specific record)

### Frontend
Plain HTML/CSS/JS, served directly by FastAPI as static files (no build step, no CORS).
- `login.html` - authenticates, stores JWT, redirects to dashboard
- `dashboard.html` - lists sessions, with Extend/Cancel controls on approved sessions; weekend/holiday extend options are shown disabled with the reason on hover instead of being clickable
- `new-request.html` - custom calendar grid; weekends, holidays, and the employee's own reserved dates are all greyed out and disabled with distinct tooltips

### Key endpoints
| Endpoint | Purpose |
|---|---|
| `POST /login` | Authenticate, receive a JWT |
| `POST /leave-request` | Submit a new request (free text or structured `start_date`/`end_date`) |
| `GET /sessions` | List the authenticated employee's past sessions |
| `POST /sessions/{thread_id}/extend` | Request a one-day extension (adjacent, working day only) |
| `POST /sessions/{thread_id}/cancel` | Cancel specific date(s) from an approved session |
| `POST /sessions/{thread_id}/resolve-mixed` | Resolve a pending mixed-conflict choice |
| `GET /holidays` | List official holidays in a date range |
| `GET /my-leave-dates` | The employee's own reserved dates in a range (for calendar rendering) |

### Deliberate failure testing
The mentor's requirement to "deliberately fail an agent" was tested across several real scenarios: missing/unclear dates, a simulated Analysis Agent crash, a Research Agent transient failure that recovers on retry, and a simulated full database outage. In every case the Coordinator's deterministic retry-then-finish logic prevented an infinite loop or a raw crash, and a top-level `try/except` around the graph invocation acts as a second safety net in the FastAPI endpoint itself.

### Known limitations
- No role field in the JWT yet (`employee` vs `manager`) - a natural Milestone 4 feature
- No manager-facing interface - escalations are recorded and locked correctly, but there's no approval screen yet
- A full request involves several sequential LLM calls (Coordinator re-invoked after every worker), so a request takes roughly 30-60 seconds - acceptable for a demo, worth being aware of

### Real bugs found and fixed (documented honestly)
- **Retry limit not enforced**: the Coordinator's LLM knew a retry limit existed but not the actual number, so it retried past the intended cap - fixed by moving the check into deterministic Python
- **In-memory checkpointer gap**: `MemorySaver` silently lost state between separate HTTP requests - switched to `PostgresSaver` after this was caught through deliberate cross-request testing
- **Reused password hash**: all seeded employees initially shared one bcrypt hash due to `hashpw()` being called once and reused - fixed to hash independently per employee
- **Outcome-detection bug**: `.startswith("APPROVE")` checks silently failed whenever the LLM wrapped its answer in markdown (`**APPROVE**`), skipping balance deduction and history recording - fixed with a single shared, markdown-tolerant `detect_decision_outcome()` function, replacing two duplicated, brittle call sites
- **Weekend/holiday extension bug**: a one-day extension only checked date adjacency, never whether the date was an actual working day, so extending onto a Sunday or official holiday was incorrectly approved - fixed by adding an explicit working-day check to `validate_single_day_extension`, reusing the same holiday data the rest of the system already relies on