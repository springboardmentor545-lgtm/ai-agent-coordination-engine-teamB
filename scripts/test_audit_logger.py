import sys
sys.path.append(".")

from observability.audit_logger import log_event
from db.queries import get_audit_logs_for_thread
TEST_THREAD_ID = "test-audit-logger-thread"

print("Logging a few sample events...\n")

log_event(thread_id=TEST_THREAD_ID, agent_name="Coordinator", action="agent_started",
          employee_id="EMP1001")

log_event(thread_id=TEST_THREAD_ID, agent_name="Research Agent", action="tool_called",
          tool_name="fetch_leave_balance", duration_ms=320, employee_id="EMP1001")

log_event(thread_id=TEST_THREAD_ID, agent_name="Research Agent", action="agent_completed",
          duration_ms=1450, employee_id="EMP1001")

log_event(thread_id=TEST_THREAD_ID, agent_name="Analysis Agent", action="agent_failed",
          status="failure", detail="simulated failure for testing", employee_id="EMP1001")

print("\nReading back from audit_logs for this thread_id:\n")
rows = get_audit_logs_for_thread(TEST_THREAD_ID)
for row in rows:
    print(row)

print(f"\nTotal rows found: {len(rows)} (expected 4)")