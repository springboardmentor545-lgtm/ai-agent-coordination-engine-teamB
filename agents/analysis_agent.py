import json
from agents.base_agent import Agent
from tools.analysis_tools import evaluate_leave_policy

analysis_worker = Agent(
    name="Analysis Agent",
    tools=[evaluate_leave_policy],
    system_instruction=(
        "You are an Analysis Agent for an employee leave approval system. "
        "You will be given structured research data (leave balance, team calendar, "
        "department size) and the requested leave dates. "
        "Your job is to call the evaluate_leave_policy tool with the EXACT values provided "
        "to you — do not estimate, guess, or recalculate any numbers yourself. "
        "Pass the leave_balance, team_calendar, and department_size exactly as given. "
        "After getting the tool result, explain what it means in plain language: "
        "whether notice period, balance, and team conflict rules passed or failed, and why. "
        "Do not make a final approve/reject/escalate decision — that is not your job."
    )
)

def analysis_agent(state):
    state["error"] = None
    try:
        raw_data = state["research"]["raw_data"]
        balance_info = raw_data.get("fetch_leave_balance", {})
        team_calendar = raw_data.get("fetch_team_calendar", [])
        dept_size_data = raw_data.get("fetch_department_size", {})
        department_size = dept_size_data.get("department_size", 0) if isinstance(dept_size_data, dict) else 0

        task = (
            f"Evaluate this leave request against policy.\n\n"
            f"Request date (today): {state['request_date']}\n"
            f"Requested start date: {state['start_date']}\n"
            f"Requested end date: {state['end_date']}\n"
            f"Employee leave balance: {balance_info.get('leave_balance')}\n"
            f"Team calendar conflicts (raw data): {json.dumps(team_calendar)}\n"
            f"Department size: {department_size}\n\n"
            f"Call evaluate_leave_policy with these exact values, then explain the results."
        )

        result = analysis_worker.think_with_trace(task)
        messages = result["messages"]
        narrative = messages[-1].content

        from langchain_core.messages import ToolMessage
        rule_results = {}
        for msg in messages:
            if isinstance(msg, ToolMessage) and msg.name == "evaluate_leave_policy":
                try:
                    rule_results = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                except (json.JSONDecodeError, TypeError):
                    rule_results = msg.content

        if not rule_results:
            raise ValueError("Policy evaluation tool did not return results.")

        state["analysis"] = {
            "narrative": narrative,
            "rule_results": rule_results,
        }
        state["completed_steps"] = state.get("completed_steps", []) + ["analysis"]
    except Exception as e:
        state["error"] = f"analysis: {str(e)}"
    return state