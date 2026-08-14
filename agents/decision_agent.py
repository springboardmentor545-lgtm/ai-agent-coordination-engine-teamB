import re
from tools.registry import TOOL_REGISTRY
from .tool_router import select_tool

class DecisionAgent:
    def execute(self, request: str):
        tool_name = select_tool(request)

        if tool_name == "unknown":
            return {
                "status": "needs_clarification",
                "tool": None,
                "message": "I could not determine which enterprise tool should handle this request.",
            }

        try:
            if tool_name == "calculator":
                expression = re.sub(r"(?i)^\s*(calculate|compute)\s*", "", request).strip()
                result = TOOL_REGISTRY[tool_name](expression)

            elif tool_name == "weather":
                city = re.sub(
                    r"(?i)^.*?(weather|temperature|forecast)\s*(in|for)?\s*",
                    "", request
                ).strip()
                result = TOOL_REGISTRY[tool_name](city)

            else:
                match = re.search(
                    r"(?i)(?:convert\s+)?([0-9]+(?:\.[0-9]+)?)\s*([A-Z]{3})\s*(?:to|in)\s*([A-Z]{3})",
                    request
                )
                if not match:
                    return {
                        "status": "needs_clarification",
                        "tool": tool_name,
                        "message": "Use a format such as: convert 100 USD to INR.",
                    }
                amount, source, target = match.groups()
                result = TOOL_REGISTRY[tool_name](float(amount), source, target)

            return {"status": "success", "tool": tool_name, "result": result}

        except (ValueError, RuntimeError) as exc:
            return {"status": "error", "tool": tool_name, "message": str(exc)}
