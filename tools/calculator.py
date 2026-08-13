from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    Performs basic mathematical calculations.
    Example: 25 * 4 or 100 / 5
    """

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"

    except Exception:
        return "Error: Invalid mathematical expression."