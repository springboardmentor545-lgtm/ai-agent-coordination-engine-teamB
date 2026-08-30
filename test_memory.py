from memory.short_term_memory import ShortTermMemory

memory = ShortTermMemory()

memory.add(
    "Convert 100 USD to INR",
    "100 USD is approximately 9539 INR"
)

memory.add(
    "What was my previous request?",
    "Your previous request was currency conversion."
)

print("\nSHORT-TERM MEMORY:")
print(memory.get_history())