import sys
sys.path.append(".")

from db.queries import get_employee_password_hash

print("EMP1001 hash:", get_employee_password_hash("EMP1001"))
print("Nonexistent employee:", get_employee_password_hash("EMP9999"))