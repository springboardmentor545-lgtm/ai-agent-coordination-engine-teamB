from graph.leave_approval_graph import leave_approval_graph
from db.queries import create_or_update_session, deduct_leave_balance, record_leave_history, save_long_term_memory


def resolve_mixed_request(thread_id: str, choice: str) -> dict:
    """
    Resolve a pending mixed-conflict choice for a session.
    choice must be 'partial' or 'escalate_all'.
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = leave_approval_graph.get_state(config)
    state = snapshot.values

    if not state.get("mixed_choice_pending"):
        return {"error": "No pending mixed-conflict choice found for this session."}

    split_info = state.get("mixed_split_info")
    employee_id = state["employee_id"]
    reason = state.get("fetched_data", {}).get("reason", "not specified")
    clean_days = split_info["clean_days"]
    conflicting_days = split_info["conflicting_days"]

    if choice == "partial":
        approved_thread_id = f"{thread_id}-approved"
        escalated_thread_id = f"{thread_id}-escalated"

        working_days = len(clean_days)
        if working_days > 0:
            deduct_leave_balance(employee_id, working_days)
        record_leave_history(employee_id, clean_days[0], clean_days[-1], "approved", reason)

        create_or_update_session(
            thread_id=approved_thread_id, employee_id=employee_id,
            start_date=clean_days[0], end_date=clean_days[-1],
            decision_outcome="APPROVE", reason=reason,
        )
        save_long_term_memory(employee_id, "leave_decision", {
            "decision": "APPROVE", "start_date": clean_days[0], "end_date": clean_days[-1],
            "summary": f"Partial approval: clean days {clean_days} approved; {conflicting_days} escalated separately.",
        })

        create_or_update_session(
            thread_id=escalated_thread_id, employee_id=employee_id,
            start_date=conflicting_days[0], end_date=conflicting_days[-1],
            decision_outcome="ESCALATE", reason=reason,
        )
        save_long_term_memory(employee_id, "leave_decision", {
            "decision": "ESCALATE", "start_date": conflicting_days[0], "end_date": conflicting_days[-1],
            "summary": f"Escalated due to team conflict: {conflicting_days}. Manager review needed.",
        })

        message = (
            f"Your clean days ({', '.join(clean_days)}) have been approved. "
            f"Your conflicting day(s) ({', '.join(conflicting_days)}) have been escalated "
            f"to your manager for review as a separate request."
        )
        leave_approval_graph.update_state(config, {"decision_outcome": "APPROVE", "completed_steps": ["planning", "research", "analysis", "decision"]})
        return {
            "outcome": "partial",
            "approved_thread_id": approved_thread_id,
            "escalated_thread_id": escalated_thread_id,
            "message": message,
        }

    elif choice == "escalate_all":
        create_or_update_session(
            thread_id=thread_id, employee_id=employee_id,
            start_date=split_info["full_range_start"], end_date=split_info["full_range_end"],
            decision_outcome="ESCALATE", reason=reason,
        )
        save_long_term_memory(employee_id, "leave_decision", {
            "decision": "ESCALATE", "start_date": split_info["full_range_start"], "end_date": split_info["full_range_end"],
            "summary": f"Entire request escalated as one, without partial approval, due to conflict on {conflicting_days}.",
        })
        message = (
            f"Your entire request ({split_info['full_range_start']} to {split_info['full_range_end']}) "
            f"has been escalated to your manager for review."
        )
        leave_approval_graph.update_state(config, {"decision_outcome": "ESCALATE", "completed_steps": ["planning", "research", "analysis", "decision"]})
        return {
            "outcome": "escalate_all",
            "thread_id": thread_id,
            "message": message,
        }

    else:
        return {"error": "Invalid choice. Must be 'partial' or 'escalate_all'."}