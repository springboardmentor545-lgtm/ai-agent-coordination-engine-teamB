import sys
sys.path.append(".")

from agents.coordinator_agent import coordinator_agent

print("--- Test 1: Fresh request, nothing done yet ---")
state1 = {"completed_steps": [], "error": None, "retry_count": {}}
result1 = coordinator_agent(state1)
print(result1["coordinator_decision"])

print("\n--- Test 2: Planning done, should dispatch research ---")
state2 = {"completed_steps": ["planning"], "error": None, "retry_count": {}}
result2 = coordinator_agent(state2)
print(result2["coordinator_decision"])

print("\n--- Test 3: Research failed once, should retry ---")
state3 = {"completed_steps": ["planning"], "error": "research: database connection failed", "retry_count": {"research": 0}}
result3 = coordinator_agent(state3)
print(result3["coordinator_decision"])

print("\n--- Test 4: Research failed twice already, should finish ---")
state4 = {"completed_steps": ["planning"], "error": "research: database connection failed", "retry_count": {"research": 1}}
result4 = coordinator_agent(state4)
print(result4["coordinator_decision"])

print("\n--- Test 5: All done, should finish ---")
state5 = {"completed_steps": ["planning", "research", "analysis", "decision"], "error": None, "retry_count": {}}
result5 = coordinator_agent(state5)
print(result5["coordinator_decision"])