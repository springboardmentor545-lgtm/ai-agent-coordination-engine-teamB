import sys
sys.path.append(".")

from db.queries import get_leave_balance, get_team_calendar, get_department_size
from agents_logic.policy_rules import check_policy_rules

# Test 1: Suhani Mishra (low balance) requesting 5 days, plenty of notice
balance_info = get_leave_balance("EMP1004")
calendar = get_team_calendar("Marketing", "2026-10-01", "2026-10-05")
dept_size = get_department_size("Marketing")

result = check_policy_rules(
    request_date="2026-09-01",
    start_date="2026-10-01",
    end_date="2026-10-05",
    leave_balance=balance_info["leave_balance"],
    team_calendar=calendar,
    department_size=dept_size,
)
print("--- Test 1: Suhani Mishra, low balance ---")
print(result)

# Test 2: Mahi Joshi requesting during the known conflict window (Sept 10-12)
balance_info2 = get_leave_balance("EMP1001")
calendar2 = get_team_calendar("Engineering", "2026-09-10", "2026-09-12")
dept_size2 = get_department_size("Engineering")

result2 = check_policy_rules(
    request_date="2026-09-05",
    start_date="2026-09-10",
    end_date="2026-09-12",
    leave_balance=balance_info2["leave_balance"],
    team_calendar=calendar2,
    department_size=dept_size2,
)
print("\n--- Test 2: Mahi Joshi, team conflict window ---")
print(result2)

# Test 3: Short notice case
result3 = check_policy_rules(
    request_date="2026-09-08",
    start_date="2026-09-09",
    end_date="2026-09-10",
    leave_balance=20,
    team_calendar=[],
    department_size=5,
)
print("\n--- Test 3: Short notice ---")
print(result3)