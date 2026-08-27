import sys
sys.path.append(".")

from db.queries import save_long_term_memory, get_long_term_memory

save_long_term_memory("EMP1001", "leave_decision", {
    "decision": "ESCALATE",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
    "reason": "40% team conflict",
})

save_long_term_memory("EMP1001", "leave_decision", {
    "decision": "APPROVE",
    "start_date": "2026-09-10",
    "end_date": "2026-09-13",
    "reason": "All policy checks passed",
})

print("--- Recent memory for EMP1001 ---")
for record in get_long_term_memory("EMP1001"):
    print(record)