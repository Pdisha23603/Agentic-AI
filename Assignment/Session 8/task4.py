# ============================================
# Task 4: Weather Assistant
# ============================================

import requests

API_KEY = "YOUR_OPENWEATHER_API_KEY"

# Function to fetch weather
def get_weather(city_name):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        return data["main"]["temp"]

    else:
        return None


# Function for advisory
def weather_advisory(temp_celsius):

    if temp_celsius < 20:
        return "Carry an umbrella ☔"

    elif temp_celsius > 30:
        return "Stay hydrated 💧"

    else:
        return "Weather is pleasant 😊"


# Main Weather Assistant
city = input("Enter city name: ")

temperature = get_weather(city)

if temperature is not None:

    print("\nWeather Assistant")
    print("-" * 35)
    print(f"City        : {city}")
    print(f"Temperature : {temperature}°C")
    print(f"Advisory    : {weather_advisory(temperature)}")

else:
    print("Unable to fetch weather information.")