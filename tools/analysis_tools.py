import json
from langchain_core.tools import tool
from agents_logic.policy_rules import check_policy_rules


@tool
def evaluate_leave_policy(
    request_date: str,
    start_date: str,
    end_date: str,
    leave_balance: int,
    team_calendar: list,
    department_size: int,
    holidays: list,
) -> str:
    """Evaluate a leave request against company policy rules: minimum notice period (3 days),
    leave balance sufficiency, and team conflict threshold (30% of department on leave).
    Weekends and official company holidays are automatically excluded from the day count
    and from conflict calculations. All dates must be in YYYY-MM-DD format."""
    result = check_policy_rules(
        request_date, start_date, end_date, leave_balance, team_calendar, department_size, holidays
    )
    return json.dumps(result)