import requests


def get_weather(city: str) -> str:
    """
    Fetches current weather for a given city using Open-Meteo (free, no API key).
    Returns a plain-text summary, or an error message if something goes wrong.
    """
    try:
        # Step 1: Convert city name to coordinates using Open-Meteo's geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Sorry, I couldn't find a location called '{city}'. Please check the spelling."

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_name = location["name"]
        country = location.get("country", "")

        # Step 2: Fetch current weather for those coordinates
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = requests.get(
            weather_url,
            params={"latitude": lat, "longitude": lon, "current_weather": True},
            timeout=10
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get("current_weather")
        if not current:
            return f"Weather data is currently unavailable for {resolved_name}."

        temp = current["temperature"]
        windspeed = current["windspeed"]

        return (
            f"The current weather in {resolved_name}, {country} is "
            f"{temp}°C with wind speed of {windspeed} km/h."
        )

    except requests.exceptions.Timeout:
        return "The weather service took too long to respond. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Could not reach the weather service due to a network error: {e}"
    except (KeyError, IndexError, ValueError):
        return "Received an unexpected response from the weather service. Please try again."


# Quick standalone test — only runs when this file is executed directly
if __name__ == "__main__":
    print(get_weather("Pune"))
    print(get_weather("London"))
    print(get_weather("asdkjqwe"))  # invalid city, tests error handling


from langchain.tools import tool


@tool
def weather_tool(city: str) -> str:
    """Get the current weather for a given city. Use this when the user asks about current weather, temperature, or wind conditions in a specific place."""
    return get_weather(city)