import sys
sys.path.append(".")

import psycopg2, os
from dotenv import load_dotenv
from graph.leave_approval_graph import leave_approval_graph

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Manually insert a conflict for EMP1007 (Marketing) on just ONE day within our test range
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute(
    "INSERT INTO team_calendar (employee_id, leave_date, status) VALUES (%s, %s, %s);",
    ("EMP1007", "2026-09-22", "on_leave")
)
conn.commit()
cursor.close()
conn.close()
print("Injected a conflict for EMP1007 on Sept 22 (Marketing, dept size 3 -> 1/3 = 33% > 30%)")

thread_config = {"configurable": {"thread_id": "test-mixed-real"}, "recursion_limit": 25}

initial_state = {
    "user_query": "I want to take leave from Sept 21 to Sept 23",
    "employee_id": "EMP1005",
    "completed_steps": [],
    "retry_count": {},
    "error": None,
}

result = leave_approval_graph.invoke(initial_state, config=thread_config)

print("\n--- Completed Steps ---")
print(result["completed_steps"])
print("\n--- Mixed choice pending? ---")
print(result.get("mixed_choice_pending"))
print("\n--- Split info ---")
print(result.get("mixed_split_info"))
print("\n--- Final Response ---")
print(result.get("final_response"))