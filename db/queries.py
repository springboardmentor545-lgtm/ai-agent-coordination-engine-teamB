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