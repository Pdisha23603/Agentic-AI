# ============================================
# Task 5: Weather Assistant with Error Handling
# ============================================

import requests

API_KEY = "YOUR_OPENWEATHER_API_KEY"

# Fetch weather from API
def get_weather(city_name):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Check API response code
    if str(data.get("cod")) == "200":
        return data["main"]["temp"]

    else:
        return None


# Weather advisory
def weather_advisory(temp_celsius):

    if temp_celsius < 20:
        return "Carry an umbrella ☔"

    elif temp_celsius > 30:
        return "Stay hydrated 💧"

    else:
        return "Weather is pleasant 😊"


# Main Program
print("========== Weather Assistant ==========")

city = input("Enter city name: ")

temperature = get_weather(city)

if temperature is None:

    print("\nCity not found, please try again.")

else:

    print("\nWeather Report")
    print("-" * 35)
    print(f"City        : {city}")
    print(f"Temperature : {temperature}°C")
    print(f"Advisory    : {weather_advisory(temperature)}")