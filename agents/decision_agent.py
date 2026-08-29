from db.queries import create_or_update_session
from db.queries import save_long_term_memory, deduct_leave_balance, record_leave_history
from agents.base_agent import Agent

decision_worker = Agent(
    name="Decision Agent",
    tools=[],
    system_instruction=(
        "You are a Decision Agent for an employee leave approval system. "
        "You will be given the results of a policy analysis (notice period, leave balance, "
        "and team conflict checks). Based on these results, you must give a final decision: "
        "APPROVE, REJECT, or ESCALATE.\n\n"
        "Use this reasoning:\n"
        "- If balance_ok is False, the request cannot be granted as-is: REJECT, and explain "
        "the employee does not have enough leave balance.\n"
        "- If notice_ok is False, this is a short-notice request. ESCALATE to the manager "
        "rather than auto-rejecting, since managers may allow exceptions for urgent reasons.\n"
        "- If team_conflict is True (more than 30% of the department on leave), ESCALATE to "
        "the manager, since this is a scheduling tradeoff a manager should judge, not an "
        "automatic rejection.\n"
        "- If all three checks pass (notice_ok, balance_ok both True, team_conflict False), "
        "APPROVE the request.\n"
        "- If multiple issues exist, mention all of them but choose REJECT if balance is "
        "insufficient (hardest constraint), otherwise ESCALATE if any other issue exists.\n\n"
        "Always state the final decision clearly as one word (APPROVE, REJECT, or ESCALATE) "
        "followed by a short, clear explanation for the employee."
    )
)

def decision_agent(state):
    state["error"] = None
    try:
        rule_results = state["analysis"]["rule_results"]
        task = (
            f"Here are the policy analysis results for this leave request:\n"
            f"{rule_results}\n\n"
            f"Give the final decision (APPROVE, REJECT, or ESCALATE) with a clear explanation."
        )
        result = decision_worker.think(task)

        # Detect outcome from the RAW result, before any delta note is prepended
        outcome = "UNKNOWN"
        if result.upper().startswith("APPROVE"):
            outcome = "APPROVE"
        elif result.upper().startswith("REJECT"):
            outcome = "REJECT"
        elif result.upper().startswith("ESCALATE"):
            outcome = "ESCALATE"

        if state.get("delta_note"):
            result = f"{state['delta_note']}\n\n{result}"

        state["decision"] = result
        state["completed_steps"] = state.get("completed_steps", []) + ["decision"]
        state["final_response"] = result
        state["decision_outcome"] = outcome

        save_long_term_memory(state["employee_id"], "leave_decision", {
            "decision": outcome,
            "start_date": state.get("start_date"),
            "end_date": state.get("end_date"),
            "summary": result,
        })

        create_or_update_session(
            thread_id=state.get("thread_id", "unknown"),
            employee_id=state["employee_id"],
            start_date=state.get("start_date"),
            end_date=state.get("end_date"),
            decision_outcome=outcome,
            reason=state.get("fetched_data", {}).get("reason", "not specified"),
        )

        # On approval, deduct the actual working days from balance and record history
        if outcome == "APPROVE":
            rule_results = state.get("analysis", {}).get("rule_results", {})
            working_days = rule_results.get("requested_days", 0)
            if working_days > 0:
                deduct_leave_balance(state["employee_id"], working_days)
            reason = state.get("fetched_data", {}).get("reason", "not specified")
            record_leave_history(
                state["employee_id"],
                state.get("start_date"),
                state.get("end_date"),
                "approved",
                reason,
            )
    except Exception as e:
        state["error"] = f"decision: {str(e)}"
    return state