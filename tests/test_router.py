from agents.tool_router import select_tool

def test_weather():
    assert select_tool("weather in Hyderabad") == "weather"

def test_currency():
    assert select_tool("convert 100 USD to INR") == "currency"

def test_calculator():
    assert select_tool("calculate 20 * 5") == "calculator"
