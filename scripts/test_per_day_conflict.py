import sys
sys.path.append(".")

from agents_logic.policy_rules import check_policy_rules

# Craft team_calendar where ONLY Sept 15 has a conflict (2 people), 16-17 are clean
team_calendar = [
    {"employee_id": "EMP1002", "leave_date": "2026-09-15", "status": "on_leave"},
    {"employee_id": "EMP1003", "leave_date": "2026-09-15", "status": "on_leave"},
]

result = check_policy_rules(
    request_date="2026-09-01",
    start_date="2026-09-15",
    end_date="2026-09-17",
    leave_balance=20,
    team_calendar=team_calendar,
    department_size=5,
    holidays=[],
)

print("--- Overall ---")
print("team_conflict:", result["team_conflict"])
print("conflict_ratio:", result["conflict_ratio"])

print("\n--- Day by day ---")
for day in result["day_by_day_status"]:
    print(day)

print("\nClean days:", result["clean_days"])
print("Conflicting days:", result["conflicting_days"])