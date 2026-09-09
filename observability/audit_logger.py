import logging
from db.queries import insert_audit_log

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("audit")


def log_event(thread_id, agent_name, action, status="success",
              employee_id=None, tool_name=None, duration_ms=None, detail=None):
    """
    Single entry point for all audit logging. Prints a readable console line
    (for live visibility, per sir's request) and writes the same event to the
    audit_logs table (for the per-session Logging view and Monitoring page).
    Never raises - a logging failure must never break a real leave request.
    """
    short_id = thread_id[:8] if thread_id else "unknown"
    label = f"tool '{tool_name}'" if tool_name else action
    timing = f" ({duration_ms}ms)" if duration_ms is not None else ""
    tag = " [FAILED]" if status == "failure" else ""
    note = f" - {detail}" if detail else ""

    message = f"[{short_id}] {agent_name} -> {label}{timing}{tag}{note}"
    if status == "failure":
        logger.error(message)
    else:
        logger.info(message)

    insert_audit_log(
        thread_id=thread_id, agent_name=agent_name, action=action, status=status,
        employee_id=employee_id, tool_name=tool_name, duration_ms=duration_ms, detail=detail
    )