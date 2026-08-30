import sys
sys.path.append(".")

from datetime import datetime
from agents_logic.policy_rules import check_policy_rules, split_mixed_request

team_calendar = [
    {"employee_id": "EMP1002", "leave_date": "2026-09-22", "status": "on_leave"},
    {"employee_id": "EMP1003", "leave_date": "2026-09-22", "status": "on_leave"},
]

result = check_policy_rules(
    request_date="2026-09-01",
    start_date="2026-09-21",
    end_date="2026-09-23",
    leave_balance=20,
    team_calendar=team_calendar,
    department_size=5,
    holidays=[],
)

print("Clean days:", result["clean_days"])
print("Conflicting days:", result["conflicting_days"])

s_date = datetime.strptime("2026-09-21", "%Y-%m-%d").date()
e_date = datetime.strptime("2026-09-23", "%Y-%m-%d").date()

split_result = split_mixed_request(result["clean_days"], result["conflicting_days"], set(), s_date, e_date)
print("\n--- Split result ---")
print(split_result)