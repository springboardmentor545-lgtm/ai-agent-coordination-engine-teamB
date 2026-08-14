from .calculator import calculate
from .currency import convert_currency
from .weather import get_weather

TOOL_REGISTRY = {
    "calculator": calculate,
    "currency": convert_currency,
    "weather": get_weather,
}
