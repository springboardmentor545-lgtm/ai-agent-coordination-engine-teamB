import sys
sys.path.append(".")

from agents_logic.policy_rules import compute_cancellation

print("--- Valid: cancel the middle day (16) from approved 15-17 ---")
result = compute_cancellation("2026-09-15", "2026-09-17", [], ["2026-09-16"], set())
print(result)

print("\n--- Invalid: trying to cancel a date outside the approved range ---")
result = compute_cancellation("2026-09-15", "2026-09-17", [], ["2026-09-20"], set())
print(result)

print("\n--- Invalid: trying to cancel a date already cancelled ---")
result = compute_cancellation("2026-09-15", "2026-09-17", ["2026-09-16"], ["2026-09-16"], set())
print(result)

print("\n--- Valid: cancel entire range ---")
result = compute_cancellation("2026-09-15", "2026-09-17", [], ["2026-09-15", "2026-09-16", "2026-09-17"], set())
print(result)