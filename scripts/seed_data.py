import os
import psycopg2
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def reset_and_seed():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # 1. Clear child tables first (foreign key order), then parent
    cursor.execute("DELETE FROM long_term_memory;")
    cursor.execute("DELETE FROM team_calendar;")
    cursor.execute("DELETE FROM leave_history;")
    cursor.execute("DELETE FROM employees;")

    # 2. Insert employees
    employees = [
        ("EMP1001", "Mahi Joshi", "Engineering", "EMP1006", 18),
        ("EMP1002", "Sagar Mehta", "Engineering", "EMP1006", 20),
        ("EMP1003", "Radha Kulkarni", "Engineering", "EMP1006", 15),
        ("EMP1004", "Suhani Mishra", "Marketing", "EMP1007", 2),
        ("EMP1005", "Kartik Sharma", "Marketing", "EMP1007", 20),
        ("EMP1006", "Anjali Verma", "Engineering", None, 20),
        ("EMP1007", "Suhani Pande", "Marketing", None, 20),
        ("EMP1008", "Raj Deshmukh", "Engineering", "EMP1006", 20),
    ]
    cursor.executemany(
        "INSERT INTO employees (employee_id, name, department, manager_id, leave_balance) VALUES (%s, %s, %s, %s, %s);",
        employees
    )

    # 3. Insert some leave history (past approved leaves)
    leave_history = [
        ("EMP1001", date(2026, 5, 10), date(2026, 5, 12), "approved", "Family function"),
        ("EMP1003", date(2026, 6, 1), date(2026, 6, 3), "approved", "Personal"),
        ("EMP1004", date(2026, 7, 15), date(2026, 7, 20), "approved", "Medical"),
    ]
    cursor.executemany(
        "INSERT INTO leave_history (employee_id, start_date, end_date, status, reason) VALUES (%s, %s, %s, %s, %s);",
        leave_history
    )

    # 4. Insert team_calendar entries for a team-conflict test scenario
    # Simulate: EMP1002 and EMP1003 already on leave during Sept 10-12, 2026
    conflict_start = date(2026, 9, 10)
    team_calendar = []
    for emp_id in ["EMP1002", "EMP1003"]:
        for i in range(3):
            team_calendar.append((emp_id, conflict_start + timedelta(days=i), "on_leave"))
    cursor.executemany(
        "INSERT INTO team_calendar (employee_id, leave_date, status) VALUES (%s, %s, %s);",
        team_calendar
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Database reset and reseeded successfully!")

if __name__ == "__main__":
    reset_and_seed()