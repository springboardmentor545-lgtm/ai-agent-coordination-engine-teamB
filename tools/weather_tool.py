from langchain.tools import tool
import os
import re
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")

@tool

def get_weather(city: str):
    """
    Get the current weather information for a city.
    Use this tool when the user asks about current weather,
    temperature, humidity, wind speed, or weather conditions.

    """

    # ----------------------------
    # Input Validation
    # ----------------------------

    if city is None:
        return {
            "success": False,
            "message": "City name is required."
        }

    city = city.strip()

    if not city:
        return {
            "success": False,
            "message": "City name cannot be empty."
        }

    # Only letters and spaces allowed
    if not re.fullmatch(r"[A-Za-z ]+", city):
        return {
            "success": False,
            "message": "City name should contain only letters and spaces."
        }

    # Minimum length check
    if len(city) < 2:
        return {
            "success": False,
            "message": "City name is too short."
        }

    # API Key validation
    if not API_KEY:
        return {
            "success": False,
            "message": "Weather API key not found."
        }

    # ----------------------------
    # API Request
    # ----------------------------

    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": API_KEY,
        "q": city
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        # API returned an error
        if "error" in data:
            return {
                "success": False,
                "message": data["error"]["message"]
            }

        # Success
        return {
            "success": True,
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"]
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Request timed out. Please try again."
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Unable to connect to the Weather API. Check your internet connection."
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Request failed: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }