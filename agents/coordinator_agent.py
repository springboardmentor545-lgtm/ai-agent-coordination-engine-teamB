import json
from agents.base_agent import Agent
from agents_logic.policy_rules import split_mixed_request
from datetime import datetime as _datetime

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

    # Deterministic gate: if Analysis just completed and the request is genuinely
    # mixed (some clean days, some conflicting days), stop and ask the employee
    # to choose, rather than letting Decision Agent auto-decide for everything.
    if completed_steps == ["planning", "research", "analysis"] and not state.get("mixed_choice_pending"):
        rule_results = state.get("analysis", {}).get("rule_results", {})
        clean_days = rule_results.get("clean_days", [])
        conflicting_days = rule_results.get("conflicting_days", [])
        if clean_days and conflicting_days:
            s_date = _datetime.strptime(state["start_date"], "%Y-%m-%d").date()
            e_date = _datetime.strptime(state["end_date"], "%Y-%m-%d").date()
            split_info = split_mixed_request(clean_days, conflicting_days, set(), s_date, e_date)
            state["mixed_choice_pending"] = True
            state["mixed_split_info"] = split_info
            state["final_response"] = (
                f"Your request for {state['start_date']} to {state['end_date']} has a mix of "
                f"clean and conflicting days. Clean days ({', '.join(clean_days)}) could be "
                f"approved now. Conflicting days ({', '.join(conflicting_days)}) would need "
                f"manager review. Would you like to: (a) approve the clean days and escalate "
                f"only the conflicting ones, or (b) escalate the entire request as one, without "
                f"any partial approval?"
            )
            state["coordinator_decision"] = {
                "action": "finish",
                "next_agent": None,
                "reasoning": "Request is mixed; awaiting employee's choice between partial approval and full escalation.",
            }
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