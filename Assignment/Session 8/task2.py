# ============================================
# Task 2: OpenWeatherMap API Weather Fetcher
# ============================================

import requests

API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(city_name):
    """
    Fetches current weather from OpenWeatherMap API.
    """

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"      # Temperature in Celsius
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        temperature = data["main"]["temp"]

        print("Current Weather")
        print("-" * 30)
        print(f"City        : {city_name}")
        print(f"Temperature : {temperature}°C")

    else:
        print("Error:", data.get("message", "Unable to fetch weather."))


# Example
get_weather("Ahmedabad")