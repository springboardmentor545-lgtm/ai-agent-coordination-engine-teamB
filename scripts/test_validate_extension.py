import sys
sys.path.append(".")

from agents_logic.policy_rules import validate_extension_dates

print("--- Valid: extend forward, approved 15-16, add 17-18 ---")
print(validate_extension_dates("2026-09-15", "2026-09-16", ["2026-09-17", "2026-09-18"]))

print("\n--- Valid: extend backward, approved 15-16, add 13-14 ---")
print(validate_extension_dates("2026-09-15", "2026-09-16", ["2026-09-13", "2026-09-14"]))

print("\n--- Invalid: gap forward, approved 15-16, add 18 (skipping 17) ---")
print(validate_extension_dates("2026-09-15", "2026-09-16", ["2026-09-18"]))

print("\n--- Invalid: mixing both directions ---")
print(validate_extension_dates("2026-09-15", "2026-09-16", ["2026-09-14", "2026-09-17"]))