import sys
sys.path.append(".")

from tools.research_tools import fetch_leave_balance, fetch_leave_history, fetch_team_calendar, fetch_department_size
from tools.analysis_tools import evaluate_leave_policy

print("--- Test 1: fetch_leave_balance ---")
print(fetch_leave_balance.invoke({"employee_id": "EMP1004"}))

print("\n--- Test 2: fetch_leave_history ---")
print(fetch_leave_history.invoke({"employee_id": "EMP1003"}))

print("\n--- Test 3: fetch_team_calendar ---")
print(fetch_team_calendar.invoke({
    "department": "Engineering",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12"
}))

print("\n--- Test 4: fetch_department_size ---")
print(fetch_department_size.invoke({"department": "Engineering"}))

print("\n--- Test 5: evaluate_leave_policy ---")
calendar = fetch_team_calendar.invoke({
    "department": "Engineering",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12"
})
print(evaluate_leave_policy.invoke({
    "request_date": "2026-09-05",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
    "leave_balance": 18,
    "team_calendar": calendar,
    "department_size": 5
}))