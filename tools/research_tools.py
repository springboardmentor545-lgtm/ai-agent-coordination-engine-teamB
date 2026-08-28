import json
from langchain_core.tools import tool
from db.queries import get_leave_balance, get_leave_history, get_team_calendar, get_department_size, get_long_term_memory
from db.queries import get_holidays_in_range

@tool
def fetch_leave_balance(employee_id: str) -> str:
    """Fetch an employee's leave balance, name, and department using their employee ID.
    Use this to check how many leave days an employee currently has available."""
    result = get_leave_balance(employee_id)
    return json.dumps(result)


@tool
def fetch_leave_history(employee_id: str) -> str:
    """Fetch an employee's past leave records (approved, rejected, or escalated) using their employee ID.
    Returns an empty list if the employee has no past leave history."""
    result = get_leave_history(employee_id)
    return json.dumps(result)


@tool
def fetch_team_calendar(department: str, start_date: str, end_date: str) -> str:
    """Fetch which employees in a given department are already on leave during a date range.
    Dates must be in YYYY-MM-DD format. Returns an empty list if no one is on leave."""
    result = get_team_calendar(department, start_date, end_date)
    return json.dumps(result)


@tool
def fetch_department_size(department: str) -> str:
    """Fetch the total number of employees in a department. Used to calculate what
    percentage of the team is on leave during a given period."""
    result = get_department_size(department)
    return json.dumps({"department_size": result})

@tool
def fetch_past_decisions(employee_id: str) -> str:
    """Fetch this employee's past leave decisions from long-term memory, from previous
    conversations. Useful for understanding patterns like how many requests they've
    made recently or what was decided before."""
    result = get_long_term_memory(employee_id)
    return json.dumps(result)

@tool
def fetch_holidays(start_date: str, end_date: str) -> str:
    """Fetch official company holidays that fall within a date range. Dates must be
    in YYYY-MM-DD format. Use this to check if any part of a leave request overlaps
    with a company holiday, so it isn't double-counted against leave balance."""
    result = get_holidays_in_range(start_date, end_date)
    return json.dumps(result)