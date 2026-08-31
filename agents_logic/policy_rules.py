from datetime import date, datetime, timedelta

def find_own_overlap_conflicts(start_date: str, end_date: str, sessions: list[dict]) -> list[dict]:
    """
    Given a requested date range and an employee's existing sessions, return any
    APPROVE or ESCALATE sessions whose active (non-cancelled) days overlap the
    requested range. REJECT sessions never block, and any individually cancelled
    day within an approved session no longer blocks either.
    """
    def date_range(s, e):
        s_date = datetime.strptime(s, "%Y-%m-%d").date()
        e_date = datetime.strptime(e, "%Y-%m-%d").date()
        days = []
        current = s_date
        while current <= e_date:
            days.append(current.isoformat())
            current += timedelta(days=1)
        return days

    requested_days = set(date_range(start_date, end_date))
    conflicts = []

    for session in sessions:
        if session.get("decision_outcome") not in ("APPROVE", "ESCALATE"):
            continue
        session_days = set(date_range(session["start_date"], session["end_date"]))
        cancelled = set(session.get("cancelled_dates") or [])
        active_days = session_days - cancelled
        overlap = requested_days & active_days
        if overlap:
            conflicts.append({
                "thread_id": session["thread_id"],
                "decision_outcome": session["decision_outcome"],
                "overlapping_dates": sorted(overlap),
            })

    return conflicts

def get_own_reserved_dates(sessions: list[dict], range_start: str, range_end: str) -> dict:
    """
    Given an employee's sessions and a display range (e.g. one calendar month),
    return a mapping of {date: decision_outcome} for every active (non-cancelled)
    day within that range that belongs to an APPROVE or ESCALATE session.
    Used by the frontend calendar to highlight and disable those dates.
    """
    reserved = {}
    for session in sessions:
        outcome = session.get("decision_outcome")
        if outcome not in ("APPROVE", "ESCALATE"):
            continue

        s_date = datetime.strptime(session["start_date"], "%Y-%m-%d").date()
        e_date = datetime.strptime(session["end_date"], "%Y-%m-%d").date()
        cancelled = set(session.get("cancelled_dates") or [])

        current = s_date
        while current <= e_date:
            iso = current.isoformat()
            if range_start <= iso <= range_end and iso not in cancelled:
                reserved[iso] = outcome
            current += timedelta(days=1)

    return reserved

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


def validate_single_day_extension(approved_start: str, approved_end: str, new_date: str):
    """
    Validate a one-day extension request. The new date must be immediately
    before approved_start or immediately after approved_end -- nothing else.
    Returns (is_valid, error_message, new_range_start, new_range_end).
    """
    a_start = datetime.strptime(approved_start, "%Y-%m-%d").date()
    a_end = datetime.strptime(approved_end, "%Y-%m-%d").date()
    n_date = datetime.strptime(new_date, "%Y-%m-%d").date()

    if n_date == a_end + timedelta(days=1):
        return True, None, a_start.isoformat(), n_date.isoformat()

    if n_date == a_start - timedelta(days=1):
        return True, None, n_date.isoformat(), a_end.isoformat()

    return False, (
        f"You can only extend by exactly one day, immediately before {approved_start} "
        f"or immediately after {approved_end}. {new_date} does not qualify."
    ), None, None

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

def split_mixed_request(clean_days: list, conflicting_days: list, holidays: set, s_date: date, e_date: date):
    """
    Given a request where some days are clean and some have team conflicts,
    prepare the two possible sub-requests for the employee to choose between:
    approving the clean days while escalating the conflicting ones, or
    escalating the entire original range as one.
    Returns None if the request is NOT actually mixed (all clean or all conflicting).
    """
    if not clean_days or not conflicting_days:
        return None

    return {
        "is_mixed": True,
        "clean_days": sorted(clean_days),
        "conflicting_days": sorted(conflicting_days),
        "full_range_start": s_date.isoformat(),
        "full_range_end": e_date.isoformat(),
    }