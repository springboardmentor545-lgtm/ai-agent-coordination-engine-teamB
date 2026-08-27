import json
from datetime import date
from agents.base_agent import Agent

planning_worker = Agent(
    name="Planning Agent",
    tools=[],
    system_instruction=(
        "You are a Planning Agent for an employee leave approval system. "
        "Given a raw user request and today's date, your job is to extract structured "
        "information and prepare a plan for the rest of the system to follow.\n\n"
        "You MUST respond with ONLY a valid JSON object, no other text, in this exact format:\n"
        '{\n'
        '  "start_date": "YYYY-MM-DD",\n'
        '  "end_date": "YYYY-MM-DD",\n'
        '  "reason": "short summary of why they are requesting leave, or \'not specified\'",\n'
        '  "plan": "a short description of what steps are needed to evaluate this request"\n'
        '}\n\n'
        "Convert any relative or informal dates (e.g. 'next Monday', 'Sept 10 to 12') into exact "
        "YYYY-MM-DD dates using today's date as reference. If the year is not mentioned, assume "
        "the nearest future occurrence of that date."
    )
)

def load_policy_document():
    with open("data/leave_policy.txt", "r") as f:
        return f.read()

def planning_agent(state):
    today = date.today().isoformat()
    task = (
        f"Today's date is {today}.\n"
        f"User request: \"{state['user_query']}\"\n\n"
        f"Extract the structured fields as instructed."
    )

    result = planning_worker.think(task)

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        parsed = {
            "start_date": None,
            "end_date": None,
            "reason": "not specified",
            "plan": "Could not parse dates from the request. Manual clarification needed.",
        }

    policy_text = load_policy_document()

    state["request_date"] = today
    state["start_date"] = parsed.get("start_date")
    state["end_date"] = parsed.get("end_date")
    state["plan"] = parsed.get("plan", "")
    state["fetched_data"] = {
        "reason": parsed.get("reason", "not specified"),
        "policy_document": policy_text,
    }
    state["completed_steps"] = state.get("completed_steps", []) + ["planning"]
    return state