from datetime import date, datetime, timedelta


def count_working_days(start: date, end: date, holidays: set) -> int:
    """Count days between start and end (inclusive) excluding weekends and holidays."""
    working_days = 0
    current = start
    while current <= end:
        is_weekend = current.weekday() >= 5  # 5 = Saturday, 6 = Sunday
        is_holiday = current.isoformat() in holidays
        if not is_weekend and not is_holiday:
            working_days += 1
        current += timedelta(days=1)
    return working_days


def check_policy_rules(
    request_date: str,
    start_date: str,
    end_date: str,
    leave_balance: int,
    team_calendar: list[dict],
    department_size: int,
    holidays: list = None,
) -> dict:
    """
    Evaluate leave request against policy rules.
    Returns a dict with rule results and an overall recommendation hint.
    """
    holidays = holidays or []
    holiday_set = set(holidays)

    req_date = datetime.strptime(request_date, "%Y-%m-%d").date()
    s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    e_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    total_calendar_days = (e_date - s_date).days + 1
    requested_days = count_working_days(s_date, e_date, holiday_set)
    notice_days = (s_date - req_date).days

    # Rule 1: Minimum notice period (3 days)
    notice_ok = notice_days >= 3

    # Rule 2: Balance sufficiency (only working days count against balance)
    balance_ok = leave_balance >= requested_days

    # Rule 3: Team conflict (30% threshold) — only count conflicts on actual working days
    conflicting_employees = len(set(
        entry["employee_id"] for entry in team_calendar
        if entry["leave_date"] not in holiday_set
        and datetime.strptime(entry["leave_date"], "%Y-%m-%d").date().weekday() < 5
    ))
    conflict_ratio = conflicting_employees / department_size if department_size > 0 else 0
    team_conflict = conflict_ratio > 0.30

    return {
        "total_calendar_days": total_calendar_days,
        "requested_days": requested_days,
        "holidays_excluded": sorted(holiday_set),
        "notice_days": notice_days,
        "notice_ok": notice_ok,
        "balance_ok": balance_ok,
        "conflicting_employees": conflicting_employees,
        "department_size": department_size,
        "conflict_ratio": round(conflict_ratio, 2),
        "team_conflict": team_conflict,
    }

def compute_extension_delta(previous_start: str, previous_end: str, new_start: str, new_end: str):
    """
    Given a previously approved date range and a newly requested date range,
    return only the NEW days that were not part of the original approval.
    Returns (delta_start, delta_end) as strings, or (None, None) if there's no new range
    (e.g. the new range is fully contained within, or identical to, the approved one).
    """
    prev_s = datetime.strptime(previous_start, "%Y-%m-%d").date()
    prev_e = datetime.strptime(previous_end, "%Y-%m-%d").date()
    new_s = datetime.strptime(new_start, "%Y-%m-%d").date()
    new_e = datetime.strptime(new_end, "%Y-%m-%d").date()

    # Case: extension after the approved range (e.g. approved 15-17, now asking 15-18)
    if new_e > prev_e:
        delta_start = max(new_s, prev_e + timedelta(days=1))
        if delta_start <= new_e:
            return delta_start.isoformat(), new_e.isoformat()

    # Case: extension before the approved range (e.g. approved 15-17, now asking 14-17)
    if new_s < prev_s:
        delta_end = min(new_e, prev_s - timedelta(days=1))
        if new_s <= delta_end:
            return new_s.isoformat(), delta_end.isoformat()

    # No new days -- fully contained within or identical to the existing approval
    return None, None