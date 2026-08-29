import json
from agents.base_agent import Agent
from db.queries import get_long_term_memory
from agents_logic.policy_rules import compute_extension_delta

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
        "EXCEPTION: if the error is from 'planning' and mentions missing or unclear dates, this is a "
        "user input problem, not a transient failure — choose action 'finish' immediately instead of retrying, "
        "since retrying won't produce different dates.\n"
        "- Once decision is in completed_steps, choose action 'finish'.\n"
    )
)

def coordinator_agent(state):
    completed_steps = state.get("completed_steps", [])
    error = state.get("error")
    retry_count = state.get("retry_count", {})

    # Deterministic delta check: if this employee has a recent APPROVE and the
    # new message asks for a different (but overlapping/adjacent) date range,
    # evaluate only the NEW days as an independent request.
    if not completed_steps == ["planning"] and not state.get("delta_applied"):
        past_records = get_long_term_memory(state["employee_id"], limit=1)
        if past_records and past_records[0]["value"].get("decision") == "APPROVE":
            prev = past_records[0]["value"]
            prev_start = prev.get("start_date")
            prev_end = prev.get("end_date")
            new_start = state.get("start_date")
            new_end = state.get("end_date")
            # Only attempt delta logic if the new request already has dates
            # (Planning hasn't run yet on a totally fresh message, so this mainly
            # applies when start_date/end_date were carried over from short-term memory)
            if prev_start and prev_end and new_start and new_end and (new_start != prev_start or new_end != prev_end):
                delta_start, delta_end = compute_extension_delta(prev_start, prev_end, new_start, new_end)
                if delta_start and delta_end:
                    state["start_date"] = delta_start
                    state["end_date"] = delta_end
                    state["delta_applied"] = True
                    state["delta_note"] = (
                        f"Your leave from {prev_start} to {prev_end} is already approved. "
                        f"Evaluating only the new portion: {delta_start} to {delta_end}."
                    )
    # Deterministic lock: once a request has been escalated or rejected,
    # do not allow further self-service modification within this conversation.
    if not completed_steps and state.get("decision_outcome") in ("ESCALATE", "REJECT"):
        if state.get("decision_outcome") == "ESCALATE":
            locked_message = (
                "Your previous leave request was escalated to your manager and is "
                "pending their review. Please wait for their decision, or contact "
                "them directly, rather than submitting a new or modified request."
            )
        else:
            locked_message = (
                "Your previous leave request was rejected. This session is now closed. "
                "If your circumstances have changed (e.g. your leave balance), please "
                "start a new leave request."
            )

        state["coordinator_decision"] = {
            "action": "finish",
            "next_agent": None,
            "reasoning": "Request is locked pending manager review after an earlier escalation.",
        }
        state["decision"] = locked_message
        state["final_response"] = locked_message
        return state

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