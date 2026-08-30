from datetime import date as _date
from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent
from agents.decision_agent import decision_worker
from agents_logic.policy_rules import validate_single_day_extension
from db.queries import get_session, create_or_update_session, deduct_leave_balance, record_leave_history, save_long_term_memory
from db.queries import lock_extend_for_session


def process_extension(thread_id: str, new_date: str, employee_id: str) -> dict:
    """
    Validate and evaluate a request to extend an already-approved leave session
    by exactly one day, either immediately before or immediately after the
    current approved range. Only modifies the session if the extension is APPROVED.
    """
    session = get_session(thread_id)
    if session is None:
        return {"error": "Session not found."}
    if session["employee_id"] != employee_id:
        return {"error": "You do not have permission to modify this session."}
    if session["decision_outcome"] != "APPROVE":
        return {"error": "Only approved leave sessions can be extended."}
    if session.get("extend_locked"):
        return {"error": "Extension is no longer available for this session. You can still cancel part or all of your approved leave."}
    is_valid, error_message, new_range_start, new_range_end = validate_single_day_extension(
        session["start_date"], session["end_date"], new_date
    )
    if not is_valid:
        return {"error": error_message}

    delta_state = {
        "user_query": f"Extend leave to include {new_date}",
        "employee_id": session["employee_id"],
        "thread_id": thread_id,
        "request_date": _date.today().isoformat(),
        "start_date": new_date,
        "end_date": new_date,
        "completed_steps": [],
        "retry_count": {},
        "error": None,
        "fetched_data": {"reason": session.get("reason", "not specified")},
    }

    delta_state = research_agent(delta_state)
    if delta_state.get("error"):
        return {"error": f"Could not evaluate extension: {delta_state['error']}"}

    delta_state = analysis_agent(delta_state)
    if delta_state.get("error"):
        return {"error": f"Could not evaluate extension: {delta_state['error']}"}

    rule_results = delta_state["analysis"]["rule_results"]
    task = (
        f"Here are the policy analysis results for this leave EXTENSION request "
        f"(a single additional day: {new_date}):\n"
        f"{rule_results}\n\n"
        f"Give the final decision (APPROVE, REJECT, or ESCALATE) with a clear explanation."
    )
    result = decision_worker.think(task)

    outcome = "UNKNOWN"
    if result.upper().startswith("APPROVE"):
        outcome = "APPROVE"
    elif result.upper().startswith("REJECT"):
        outcome = "REJECT"
    elif result.upper().startswith("ESCALATE"):
        outcome = "ESCALATE"

    if outcome == "APPROVE":
        working_days = rule_results.get("requested_days", 0)
        if working_days > 0:
            deduct_leave_balance(session["employee_id"], working_days)
        record_leave_history(
            session["employee_id"], new_date, new_date, "approved",
            session.get("reason", "not specified"),
        )
        create_or_update_session(
            thread_id=thread_id,
            employee_id=session["employee_id"],
            start_date=new_range_start,
            end_date=new_range_end,
            decision_outcome="APPROVE",
            reason=session.get("reason", "not specified"),
        )
        save_long_term_memory(session["employee_id"], "leave_decision", {
            "decision": "APPROVE",
            "start_date": new_range_start,
            "end_date": new_range_end,
            "summary": f"Extension approved, new range: {new_range_start} to {new_range_end}. {result}",
        })
        message = (
            f"Extension approved! Your leave now covers {new_range_start} to {new_range_end}. {result}"
        )
    else:
        lock_extend_for_session(thread_id)
        message = (
            f"Your original approved leave ({session['start_date']} to {session['end_date']}) "
            f"remains completely unaffected and safe. Your extension request was "
            f"{outcome.lower()}ed: {result}\n\n"
            f"Extending this leave is no longer available, but you can still cancel part "
            f"or all of your existing approved leave if needed."
        )
    return {
        "thread_id": thread_id,
        "outcome": outcome,
        "original_range": {"start_date": session["start_date"], "end_date": session["end_date"]},
        "requested_extension_date": new_date,
        "message": message,
    }