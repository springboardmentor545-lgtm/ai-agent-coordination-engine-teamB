from collections import defaultdict

_sessions = defaultdict(list)

def add_event(session_id: str, request: str, response: dict):
    _sessions[session_id].append({"request": request, "response": response})

def get_history(session_id: str):
    return list(_sessions[session_id])
