def validate_state(state):
    # Check user query
    if not state.get("user_query"):
        return False, "Error: User query is missing."

    # Check planning result
    if not state.get("plan"):
        return False, "Error: Planning Agent did not produce a plan."

    # Check research result
    if not state.get("research_result"):
        return False, "Error: Research Agent did not produce a result."

    # Check analysis result
    if not state.get("analysis"):
        return False, "Error: Analysis Agent did not produce a result."

    return True, "Validation successful."