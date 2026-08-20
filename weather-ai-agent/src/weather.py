import requests  # HTTP requests library

# Weather Tool Description to give to LLM model
weather_tool_desc = {
    "type": "function",
    "name": "get_weather",
    "description": "Get the current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or location name.",
            }
        },
        "required": ["location"],
    },
}


# Fetch Weather Data
def get_weather(location):
    """Fetch current weather for a given location."""

    # Find latitude and longitude
    lat_long_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_response = requests.get(
        lat_long_url, params={"name": location, "count": 1, "format": "json"}
    )

    geo_response.raise_for_status()

    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return {"error": "Location not found"}

    place = geo_data["results"][0]

    latitude = place["latitude"]
    longitude = place["longitude"]

    # Get weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_response = requests.get(
        weather_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
        },
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    return {
        "location": place["name"],
        "temperature": weather_data["current"]["temperature_2m"],
        "unit": "°C",
    }
