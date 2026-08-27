import json
from langchain_core.messages import ToolMessage
from agents.base_agent import Agent
from tools.research_tools import fetch_leave_balance, fetch_leave_history, fetch_team_calendar, fetch_department_size, fetch_past_decisions

research_worker = Agent(
    name="Research Agent",
    tools=[fetch_leave_balance, fetch_leave_history, fetch_team_calendar, fetch_department_size, fetch_past_decisions],
        system_instruction=(
        "You are a Research Agent for an employee leave approval system. "
        "Your job is to gather ALL facts needed to evaluate a leave request. "
        "You MUST call these tools for every request, in this order: "
        "1) fetch_leave_balance to get the employee's balance and department, "
        "2) fetch_leave_history to get their past leave records, "
        "3) fetch_team_calendar to check for scheduling conflicts during the requested dates "
        "(use the department returned by fetch_leave_balance), "
        "4) fetch_department_size to get the total team size for that same department "
        "(this is required to calculate what percentage of the team is on leave), "
        "5) fetch_past_decisions to check this employee's leave decision history from "
        "previous conversations, since this helps understand their recent leave pattern. "
        "Do not skip fetch_department_size or fetch_past_decisions — both are required "
        "for every request. "
        "After gathering all results, summarize the facts clearly. "
        "Do not make decisions or judgments — only gather and report facts."
    )
)

def research_agent(state):
    state["error"] = None
    try:
        task = (
            f"Employee ID: {state['employee_id']}. "
            f"Plan from previous step: {state.get('plan', '')}. "
            f"Gather leave balance, leave history, and team calendar conflicts relevant to this request: "
            f"{state['user_query']}"
        )

        result = research_worker.think_with_trace(task)
        messages = result["messages"]
        narrative = messages[-1].content

        raw_data = {}
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_name = msg.name
                try:
                    content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                except (json.JSONDecodeError, TypeError):
                    content = msg.content
                raw_data[tool_name] = content

        if "fetch_department_size" not in raw_data:
            department = None
            if "fetch_leave_balance" in raw_data and isinstance(raw_data["fetch_leave_balance"], dict):
                department = raw_data["fetch_leave_balance"].get("department")
            if department:
                raw_result = fetch_department_size.invoke({"department": department})
                raw_data["fetch_department_size"] = json.loads(raw_result)

        if "fetch_leave_balance" in raw_data and isinstance(raw_data["fetch_leave_balance"], dict):
            if raw_data["fetch_leave_balance"].get("error"):
                raise ValueError(raw_data["fetch_leave_balance"]["error"])

        state["research"] = {
            "narrative": narrative,
            "raw_data": raw_data,
        }
        state["completed_steps"] = state.get("completed_steps", []) + ["research"]
    except Exception as e:
        state["error"] = f"research: {str(e)}"
    return state