from memory.long_term_memory import LongTermMemory

memory = LongTermMemory()

memory.save(
    "What is my project?",
    "Development of Enterprise Workflow Platform with Decision Automation System"
)

print("\nLONG-TERM MEMORY:")
print(memory.get_memories())