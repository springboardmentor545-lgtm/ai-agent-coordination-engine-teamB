import sys
sys.path.append(".")

from db.queries import get_leave_balance, get_leave_history, get_team_calendar

print("--- Test 1: get_leave_balance (valid employee) ---")
print(get_leave_balance("EMP1004"))

print("\n--- Test 2: get_leave_balance (invalid employee) ---")
print(get_leave_balance("EMP9999"))

print("\n--- Test 3: get_leave_history ---")
print(get_leave_history("EMP1003"))

print("\n--- Test 4: get_team_calendar (should show conflict for EMP1002 & EMP1003) ---")
print(get_team_calendar("Engineering", "2026-09-10", "2026-09-12"))