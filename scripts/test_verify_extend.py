import sys
sys.path.append(".")

from db.queries import get_session, get_leave_balance

print("--- Session after extension ---")
print(get_session("abaf48d7-1b7e-480a-9858-e89d554b7f80"))

print("\n--- Balance after extension ---")
print(get_leave_balance("EMP1008"))