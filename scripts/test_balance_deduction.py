import sys
sys.path.append(".")

from db.queries import get_leave_balance, deduct_leave_balance, record_leave_history

print("--- Before deduction ---")
print(get_leave_balance("EMP1008"))

deduct_leave_balance("EMP1008", 2)

print("\n--- After deducting 2 days ---")
print(get_leave_balance("EMP1008"))

record_leave_history("EMP1008", "2026-11-01", "2026-11-02", "approved", "Test approval")
print("\nHistory record inserted successfully.")