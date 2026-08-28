import sys
sys.path.append(".")

from db.queries import get_holidays_in_range

print("--- Holidays in Sept 10-12, 2026 (should include Sept 11 test holiday) ---")
print(get_holidays_in_range("2026-09-10", "2026-09-12"))

print("\n--- Holidays in Oct 2026 (should include Gandhi Jayanti) ---")
print(get_holidays_in_range("2026-10-01", "2026-10-31"))

print("\n--- Holidays in a range with none ---")
print(get_holidays_in_range("2026-11-01", "2026-11-10"))