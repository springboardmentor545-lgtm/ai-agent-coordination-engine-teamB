import requests

def get_weather(city: str):
    city = city.strip()
    if not city:
        raise ValueError("Please provide a city name.")

    url = "https://wttr.in/" + requests.utils.quote(city) + "?format=j1"
    try:
        response = requests.get(url, headers={"User-Agent": "EnterpriseWorkflowDemo/1.0"}, timeout=8)
        response.raise_for_status()
        current = response.json()["current_condition"][0]
        return {
            "city": city,
            "temperature_c": current.get("temp_C"),
            "feels_like_c": current.get("FeelsLikeC"),
            "description": current.get("weatherDesc", [{}])[0].get("value"),
        }
    except requests.RequestException as exc:
        raise RuntimeError("Weather service is temporarily unavailable.") from exc
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Weather service returned an unexpected response.")
