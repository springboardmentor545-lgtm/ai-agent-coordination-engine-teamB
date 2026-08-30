import sys
sys.path.append(".")

from graph.leave_approval_graph import leave_approval_graph

config = {"configurable": {"thread_id": "test-mixed-real"}}
snapshot = leave_approval_graph.get_state(config)

print("--- Raw state values ---")
print(snapshot.values)