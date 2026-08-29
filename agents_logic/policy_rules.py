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

    # Rule 3: Team conflict (30% threshold), computed both overall AND per-day
    valid_conflicts = [
        entry for entry in team_calendar
        if entry["leave_date"] not in holiday_set
        and datetime.strptime(entry["leave_date"], "%Y-%m-%d").date().weekday() < 5
    ]

    conflicting_employees = len(set(entry["employee_id"] for entry in valid_conflicts))
    conflict_ratio = conflicting_employees / department_size if department_size > 0 else 0
    team_conflict = conflict_ratio > 0.30

    conflicts_by_day = {}
    for entry in valid_conflicts:
        day = entry["leave_date"]
        conflicts_by_day.setdefault(day, set()).add(entry["employee_id"])

    day_by_day_status = []
    current = s_date
    while current <= e_date:
        day_str = current.isoformat()
        is_weekend = current.weekday() >= 5
        is_holiday = day_str in holiday_set
        if is_weekend or is_holiday:
            current += timedelta(days=1)
            continue
        day_conflict_count = len(conflicts_by_day.get(day_str, set()))
        day_ratio = day_conflict_count / department_size if department_size > 0 else 0
        day_by_day_status.append({
            "date": day_str,
            "conflicting_employees": day_conflict_count,
            "conflict_ratio": round(day_ratio, 2),
            "has_conflict": day_ratio > 0.30,
        })
        current += timedelta(days=1)

    clean_days = [d["date"] for d in day_by_day_status if not d["has_conflict"]]
    conflicting_days = [d["date"] for d in day_by_day_status if d["has_conflict"]]

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
        "day_by_day_status": day_by_day_status,
        "clean_days": clean_days,
        "conflicting_days": conflicting_days,
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


def compute_cancellation(approved_start: str, approved_end: str, currently_cancelled: list, dates_to_cancel: list, holidays: set):
    """
    Given an approved date range, dates already cancelled, and new dates the employee
    wants to cancel, validate the request and compute the working days to credit back.

    Returns a dict:
      - valid: bool
      - error: str or None
      - updated_cancelled_dates: list of all cancelled dates (old + new), sorted
      - working_days_credited: int (working days among the newly cancelled dates)
      - remaining_dates: list of dates still active in the approved leave
    """
    a_start = datetime.strptime(approved_start, "%Y-%m-%d").date()
    a_end = datetime.strptime(approved_end, "%Y-%m-%d").date()

    all_approved_dates = []
    current = a_start
    while current <= a_end:
        all_approved_dates.append(current.isoformat())
        current += timedelta(days=1)

    # Validate every requested cancellation date is actually part of the approved range
    invalid_dates = [d for d in dates_to_cancel if d not in all_approved_dates]
    if invalid_dates:
        return {
            "valid": False,
            "error": f"These dates are not part of your approved leave ({approved_start} to {approved_end}): {invalid_dates}",
            "updated_cancelled_dates": currently_cancelled,
            "working_days_credited": 0,
            "remaining_dates": [],
        }

    already_cancelled_again = [d for d in dates_to_cancel if d in currently_cancelled]
    if already_cancelled_again:
        return {
            "valid": False,
            "error": f"These dates were already cancelled previously: {already_cancelled_again}",
            "updated_cancelled_dates": currently_cancelled,
            "working_days_credited": 0,
            "remaining_dates": [],
        }

    updated_cancelled = sorted(set(currently_cancelled) | set(dates_to_cancel))

    # Only count working days (not weekends/holidays) toward balance credit
    working_days_credited = sum(
        1 for d in dates_to_cancel
        if datetime.strptime(d, "%Y-%m-%d").date().weekday() < 5 and d not in holidays
    )

    remaining_dates = [d for d in all_approved_dates if d not in updated_cancelled]

    return {
        "valid": True,
        "error": None,
        "updated_cancelled_dates": updated_cancelled,
        "working_days_credited": working_days_credited,
        "remaining_dates": remaining_dates,
    }