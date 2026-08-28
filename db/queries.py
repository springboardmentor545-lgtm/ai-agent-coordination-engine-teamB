import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_leave_balance(employee_id: str) -> dict:
    """Fetch an employee's basic info and current leave balance."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT employee_id, name, department, manager_id, leave_balance FROM employees WHERE employee_id = %s;",
        (employee_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return {"error": f"No employee found with ID {employee_id}"}

    return {
        "employee_id": row[0],
        "name": row[1],
        "department": row[2],
        "manager_id": row[3],
        "leave_balance": row[4],
    }


def get_leave_history(employee_id: str) -> list[dict]:
    """Fetch past leave records for an employee."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT start_date, end_date, status, reason FROM leave_history WHERE employee_id = %s ORDER BY start_date;",
        (employee_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {"start_date": str(r[0]), "end_date": str(r[1]), "status": r[2], "reason": r[3]}
        for r in rows
    ]


def get_team_calendar(department: str, start_date: str, end_date: str) -> list[dict]:
    """Check which employees in a department are already on leave during a date range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT tc.employee_id, e.name, tc.leave_date, tc.status
        FROM team_calendar tc
        JOIN employees e ON tc.employee_id = e.employee_id
        WHERE e.department = %s AND tc.leave_date BETWEEN %s AND %s;
        """,
        (department, start_date, end_date)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {"employee_id": r[0], "name": r[1], "leave_date": str(r[2]), "status": r[3]}
        for r in rows
    ]

def get_department_size(department: str) -> int:
    """Count total employees in a department (used for team-conflict % calculation)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM employees WHERE department = %s;",
        (department,)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

import json as _json


def save_long_term_memory(employee_id: str, key: str, value: dict) -> None:
    """Store a piece of long-term memory for an employee (e.g. a past decision record)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO long_term_memory (employee_id, key, value) VALUES (%s, %s, %s);",
        (employee_id, key, _json.dumps(value))
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_long_term_memory(employee_id: str, limit: int = 5) -> list[dict]:
    """Fetch the most recent long-term memory records for an employee."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT key, value, updated_at FROM long_term_memory WHERE employee_id = %s ORDER BY updated_at DESC LIMIT %s;",
        (employee_id, limit)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    results = []
    for key, value, updated_at in rows:
        try:
            parsed_value = _json.loads(value) if isinstance(value, str) else value
        except (_json.JSONDecodeError, TypeError):
            parsed_value = value
        results.append({"key": key, "value": parsed_value, "updated_at": str(updated_at)})
    return results

def get_holidays_in_range(start_date: str, end_date: str) -> list[str]:
    """Fetch official company holiday dates that fall within a given date range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT holiday_date FROM holidays WHERE holiday_date BETWEEN %s AND %s ORDER BY holiday_date;",
        (start_date, end_date)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [str(row[0]) for row in rows]

def deduct_leave_balance(employee_id: str, days: int) -> None:
    """Deduct approved leave days from an employee's balance."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE employees SET leave_balance = leave_balance - %s WHERE employee_id = %s;",
        (days, employee_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def record_leave_history(employee_id: str, start_date: str, end_date: str, status: str, reason: str) -> None:
    """Insert a new record into leave_history when a request is finalized."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leave_history (employee_id, start_date, end_date, status, reason) VALUES (%s, %s, %s, %s, %s);",
        (employee_id, start_date, end_date, status, reason)
    )
    conn.commit()
    cursor.close()
    conn.close()