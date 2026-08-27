import json
from agents.base_agent import Agent

MAX_RETRIES = 1

coordinator_worker = Agent(
    name="Coordinator Agent",
    tools=[],
    system_instruction=(
        "You are the Coordinator Agent for a multi-agent employee leave approval system. "
        "You control the overall workflow. You do not do any research or analysis yourself — "
        "you only decide what should happen next.\n\n"
        "Available worker agents, in their normal order: planning, research, analysis, decision.\n"
        "- planning: extracts leave dates and reason from the user's request\n"
        "- research: gathers leave balance, history, and team calendar data\n"
        "- analysis: applies policy rules to the research data\n"
        "- decision: produces the final approve/reject/escalate outcome\n\n"
        "You MUST respond with ONLY a valid JSON object, no other text, in this exact format:\n"
        '{\n'
        '  "action": "dispatch_next" or "retry" or "finish",\n'
        '  "next_agent": "planning" or "research" or "analysis" or "decision" or null,\n'
        '  "reasoning": "short explanation of your decision"\n'
        '}\n\n'
        "Rules:\n"
        "- If completed_steps is empty, start with planning.\n"
        "- Normally dispatch agents in order: planning -> research -> analysis -> decision.\n"
        "- If an error is present for the most recently attempted agent, and its retry count "
        "is below max_retries_allowed, choose action 'retry' with next_agent set to that same agent.\n"
        "- Once decision is in completed_steps, choose action 'finish'.\n"
    )
)

def coordinator_agent(state):
    completed_steps = state.get("completed_steps", [])
    error = state.get("error")
    retry_count = state.get("retry_count", {})

    # Deterministic safety check — no LLM judgment for loop protection
    if error:
        failed_agent = error.split(":")[0].strip()
        current_retries = retry_count.get(failed_agent, 0)
        if current_retries >= MAX_RETRIES:
            state["coordinator_decision"] = {
                "action": "finish",
                "next_agent": None,
                "reasoning": f"{failed_agent} failed after {current_retries} retr{'y' if current_retries == 1 else 'ies'}; retry limit reached. Ending workflow gracefully.",
            }
            state["plan"] = state.get("plan") or ["planning", "research", "analysis", "decision"]
            return state

    task = (
        f"Current state summary:\n"
        f"completed_steps: {completed_steps}\n"
        f"error: {error}\n"
        f"retry_count: {retry_count}\n"
        f"max_retries_allowed: {MAX_RETRIES}\n\n"
        f"Decide the next action."
    )

    result = coordinator_worker.think(task)

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        parsed = {
            "action": "finish",
            "next_agent": None,
            "reasoning": "Coordinator response could not be parsed; ending workflow gracefully.",
        }

    if parsed.get("action") == "retry" and parsed.get("next_agent"):
        agent_name = parsed["next_agent"]
        retry_count[agent_name] = retry_count.get(agent_name, 0) + 1
        state["retry_count"] = retry_count

    state["plan"] = state.get("plan") or ["planning", "research", "analysis", "decision"]
    state["coordinator_decision"] = parsed
    return state