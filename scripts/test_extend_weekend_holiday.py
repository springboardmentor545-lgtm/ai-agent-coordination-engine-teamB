import sys
sys.path.append(".")

from agents_logic.policy_rules import validate_single_day_extension

# Approved session: Mon Sep 14 - Tue Sep 15, 2026
# Real seeded holiday: Fri Sep 11, 2026 ("Test Holiday", from scripts/seed_holidays.py)

print("--- Case 1: valid extension, genuine working day (Wed Sep 16, forward) ---")
print(validate_single_day_extension("2026-09-14", "2026-09-15", "2026-09-16", holidays=set()))

print("\n--- Case 2: weekend rejection (Sun Sep 13, backward) ---")
print(validate_single_day_extension("2026-09-14", "2026-09-15", "2026-09-13", holidays=set()))

print("\n--- Case 3: holiday rejection (Fri Sep 11 is a seeded holiday, but not adjacent here so we use a matching range) ---")
# Approved session shifted so Sep 11 is genuinely adjacent: approved Sep 9-10, extend forward to Sep 11
print(validate_single_day_extension("2026-09-09", "2026-09-10", "2026-09-11", holidays={"2026-09-11"}))

print("\n--- Case 4: non-adjacent date still rejected first (unrelated to weekend/holiday logic) ---")
print(validate_single_day_extension("2026-09-14", "2026-09-15", "2026-09-20", holidays=set()))