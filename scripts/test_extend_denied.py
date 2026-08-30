import sys
sys.path.append(".")

from services.extend_service import process_extension
from db.queries import get_session, get_leave_balance

thread_id = "abaf48d7-1b7e-480a-9858-e89d554b7f80"

print("--- Session BEFORE attempting extension ---")
print(get_session(thread_id))
print("Balance before:", get_leave_balance("EMP1008")["leave_balance"])

# Genuinely valid, contiguous date range (Sept 19-20 are weekend, so start from Sept 21)
# Ask for way more days than remaining balance to trigger a real REJECT
dates_to_add = [f"2026-09-{str(d).zfill(2)}" for d in range(19, 31)] + [f"2026-10-{str(d).zfill(2)}" for d in range(1, 9)]

result = process_extension(thread_id, dates_to_add)
print("\n--- Extension attempt result ---")
print(result)

print("\n--- Session AFTER (should be UNCHANGED if denied) ---")
print(get_session(thread_id))
print("Balance after (should be UNCHANGED if denied):", get_leave_balance("EMP1008")["leave_balance"])