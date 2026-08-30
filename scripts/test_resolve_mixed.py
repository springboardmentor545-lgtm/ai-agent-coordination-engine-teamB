import sys
sys.path.append(".")

from services.mixed_resolution_service import resolve_mixed_request
from db.queries import get_leave_balance

print("Balance before:", get_leave_balance("EMP1005")["leave_balance"])

result = resolve_mixed_request("test-mixed-real", "partial")
print("\n--- Resolution result ---")
print(result)

print("\nBalance after:", get_leave_balance("EMP1005")["leave_balance"])