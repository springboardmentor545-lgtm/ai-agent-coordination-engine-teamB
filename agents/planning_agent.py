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
    state["error"] = None
    try:
        today = date.today().isoformat()

        existing_context = ""
        if state.get("start_date") or state.get("end_date"):
            existing_context = (
                f"\n\nContext already known from earlier in this conversation:\n"
                f"Previously requested start date: {state.get('start_date')}\n"
                f"Previously requested end date: {state.get('end_date')}\n"
                f"If the new message modifies this (e.g. 'extend by a day', 'change to a different date'), "
                f"apply that change to the known dates. If the new message doesn't mention dates at all, "
                f"reuse the previously known dates unchanged."
            )

        task = (
            f"Today's date is {today}.\n"
            f"User request: \"{state['user_query']}\"\n"
            f"{existing_context}\n\n"
            f"Extract the structured fields as instructed. If the user did not give clear, "
            f"specific dates, set start_date and end_date to null (not a string like 'not specified')."
        )

        result = planning_worker.think(task)

        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            parsed = {"start_date": None, "end_date": None, "reason": "not specified", "plan": ""}

        policy_text = load_policy_document()

        new_start = parsed.get("start_date")
        new_end = parsed.get("end_date")

        # Treat any non-date-looking value as null (defensive against the LLM returning text like "not specified")
        def is_valid_date_string(val):
            if not val or not isinstance(val, str):
                return False
            try:
                from datetime import datetime as _dt
                _dt.strptime(val, "%Y-%m-%d")
                return True
            except ValueError:
                return False

        if not is_valid_date_string(new_start):
            new_start = None
        if not is_valid_date_string(new_end):
            new_end = None

        state["request_date"] = today
        state["start_date"] = new_start or state.get("start_date")
        state["end_date"] = new_end or state.get("end_date")
        state["plan"] = parsed.get("plan", "")
        state["fetched_data"] = {
            "reason": parsed.get("reason") or state.get("fetched_data", {}).get("reason", "not specified"),
            "policy_document": policy_text,
        }
        state["completed_steps"] = state.get("completed_steps", []) + ["planning"]

        # Hard stop if we still don't have usable dates after all this
        if not state["start_date"] or not state["end_date"]:
            state["error"] = "planning: Could not determine specific leave dates from the request. Please ask the employee for exact start and end dates."

    except Exception as e:
        state["error"] = f"planning: {str(e)}"
    return state