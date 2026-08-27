from datetime import date, datetime


def check_policy_rules(
    request_date: str,      # date the request is being made, e.g. today
    start_date: str,
    end_date: str,
    leave_balance: int,
    team_calendar: list[dict],
    department_size: int,
) -> dict:
    """
    Evaluate leave request against policy rules.
    Returns a dict with rule results and an overall recommendation hint.
    """
    req_date = datetime.strptime(request_date, "%Y-%m-%d").date()
    s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    e_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    requested_days = (e_date - s_date).days + 1
    notice_days = (s_date - req_date).days

    # Rule 1: Minimum notice period (3 days)
    notice_ok = notice_days >= 3

    # Rule 2: Balance sufficiency
    balance_ok = leave_balance >= requested_days

    # Rule 3: Team conflict (30% threshold)
    conflicting_employees = len(set(entry["employee_id"] for entry in team_calendar))
    conflict_ratio = conflicting_employees / department_size if department_size > 0 else 0
    team_conflict = conflict_ratio > 0.30

    return {
        "requested_days": requested_days,
        "notice_days": notice_days,
        "notice_ok": notice_ok,
        "balance_ok": balance_ok,
        "conflicting_employees": conflicting_employees,
        "department_size": department_size,
        "conflict_ratio": round(conflict_ratio, 2),
        "team_conflict": team_conflict,
    }