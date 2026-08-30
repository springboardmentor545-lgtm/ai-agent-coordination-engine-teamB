class ShortTermMemory:
    def __init__(self):
        self.history = []

    def add(self, user_query: str, response: str):
        self.history.append({
            "user_query": user_query,
            "response": response
        })

    def get_history(self):
        return self.history