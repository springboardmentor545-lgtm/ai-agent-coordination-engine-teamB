import json
import os


class LongTermMemory:

    def __init__(self, file_path="memory/memory.json"):
        self.file_path = file_path

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump([], file)

    def save(self, user_query: str, response: str):
        with open(self.file_path, "r", encoding="utf-8") as file:
            memories = json.load(file)

        memories.append({
            "user_query": user_query,
            "response": response
        })

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(memories, file, indent=4)

    def get_memories(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)