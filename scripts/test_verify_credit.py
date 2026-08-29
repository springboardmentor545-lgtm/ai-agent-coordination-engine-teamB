import sys
sys.path.append(".")

from db.queries import get_leave_balance

print(get_leave_balance("EMP1008"))