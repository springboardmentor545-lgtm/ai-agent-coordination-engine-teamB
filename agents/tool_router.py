def select_tool(request: str) -> str:
    text = request.lower()

    if any(w in text for w in ("weather", "temperature", "forecast")):
        return "weather"
    if any(w in text for w in ("convert", "currency", "usd", "inr", "eur", "gbp")):
        return "currency"
    if any(s in text for s in ("+", "-", "*", "/", "%")) or "calculate" in text:
        return "calculator"
    return "unknown"
