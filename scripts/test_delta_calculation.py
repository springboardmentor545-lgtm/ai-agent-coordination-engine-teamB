import sys
sys.path.append(".")

from agents_logic.policy_rules import compute_extension_delta

print("--- Extend after: approved 15-17, new request 15-18 ---")
print(compute_extension_delta("2026-09-15", "2026-09-17", "2026-09-15", "2026-09-18"))

print("\n--- Extend before: approved 15-17, new request 14-17 ---")
print(compute_extension_delta("2026-09-15", "2026-09-17", "2026-09-14", "2026-09-17"))

print("\n--- No change: same range ---")
print(compute_extension_delta("2026-09-15", "2026-09-17", "2026-09-15", "2026-09-17"))

print("\n--- Fully contained: approved 15-17, new request 16-16 ---")
print(compute_extension_delta("2026-09-15", "2026-09-17", "2026-09-16", "2026-09-16"))