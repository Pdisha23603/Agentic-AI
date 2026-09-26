"""
Session 24 - Task 1: Open-Meteo Weather API Integration
-------------------------------------------------------
Fetches and displays the current temperature and atmospheric conditions for a given city
using the free, public Open-Meteo Weather and Geocoding APIs (no API key required).

Open-Meteo Documentation:
- Weather Forecast API: https://open-meteo.com/en/docs
- Geocoding API: https://open-meteo.com/en/docs/geocoding-api
"""

import sys
import os
import requests
from typing import Dict, Any, Optional, Tuple

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Fallback coordinates for major cities when network geocoding is unavailable
PRESET_COORDINATES = {
    "ahmedabad": (23.0225, 72.5714, "India"),
    "mumbai": (19.0760, 72.8777, "India"),
    "delhi": (28.6139, 77.2090, "India"),
    "bengaluru": (12.9716, 77.5946, "India"),
    "pune": (18.5204, 73.8567, "India"),
    "london": (51.5074, -0.1278, "United Kingdom"),
    "new york": (40.7128, -74.0060, "United States"),
    "tokyo": (35.6762, 139.6503, "Japan"),
    "sydney": (-33.8688, 151.2093, "Australia"),
    "paris": (48.8566, 2.3522, "France"),
}

# WMO Weather Interpretation Codes (WW)
WMO_WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def geocode_city(city_name: str, timeout: int = 8) -> Tuple[float, float, str, str]:
    """
    Resolves a city name to latitude, longitude, resolved name, and country using Open-Meteo Geocoding API.
    Falls back to preset coordinates if network is unreachable or city is not found.
    """
    clean_city = city_name.strip()
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": clean_city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results")
            if results and len(results) > 0:
                best = results[0]
                lat = float(best["latitude"])
                lon = float(best["longitude"])
                name = best.get("name", clean_city)
                country = best.get("country", "")
                return lat, lon, name, country
    except Exception as e:
        # Fall back to preset dictionary on network or parsing error
        pass

    # Preset coordinate lookup
    normalized_key = clean_city.lower()
    if normalized_key in PRESET_COORDINATES:
        lat, lon, country = PRESET_COORDINATES[normalized_key]
        return lat, lon, clean_city.title(), country

    # Default to Ahmedabad if entirely unknown
    return 23.0225, 72.5714, clean_city.title(), "India (Default)"


def get_current_weather(
    city_name: str = "Ahmedabad",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Fetches the current temperature and conditions for a city using Open-Meteo Forecast API.

    Args:
        city_name: Name of the city (e.g., 'Ahmedabad', 'Mumbai', 'London').
        latitude: Optional direct latitude coordinate.
        longitude: Optional direct longitude coordinate.
        timeout: Network timeout in seconds.

    Returns:
        Dict with keys: city, country, latitude, longitude, temperature, unit,
                        humidity, apparent_temperature, wind_speed, weather_description, icon, raw_data.
    """
    resolved_country = ""
    if latitude is None or longitude is None:
        lat, lon, resolved_city, resolved_country = geocode_city(city_name, timeout=timeout)
    else:
        lat, lon, resolved_city = latitude, longitude, city_name

    forecast_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "is_day",
        ],
        "timezone": "auto",
    }

    try:
        response = requests.get(forecast_url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        temperature = current.get("temperature_2m")
        temp_unit = data.get("current_units", {}).get("temperature_2m", "°C")
        humidity = current.get("relative_humidity_2m")
        apparent_temp = current.get("apparent_temperature")
        wind_speed = current.get("wind_speed_10m")
        wind_unit = data.get("current_units", {}).get("wind_speed_10m", "km/h")
        weather_code = current.get("weather_code", 0)

        desc, icon = WMO_WEATHER_CODES.get(weather_code, ("Fair", "🌤️"))

        return {
            "success": True,
            "city": resolved_city,
            "country": resolved_country,
            "latitude": lat,
            "longitude": lon,
            "temperature": temperature,
            "unit": temp_unit,
            "apparent_temperature": apparent_temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_unit": wind_unit,
            "weather_code": weather_code,
            "weather_description": desc,
            "icon": icon,
            "timestamp": current.get("time"),
            "raw_data": data,
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "city": city_name,
            "error": f"Failed to retrieve weather data from Open-Meteo API: {str(e)}",
            "temperature": None,
            "unit": "°C",
        }


def display_weather_report(weather_info: Dict[str, Any]) -> None:
    """Prints a styled weather dashboard summary to standard output."""
    print("=" * 60)
    print(" 🌤️  OPEN-METEO WEATHER REPORT (PERSONAL ASSISTANT TOOL)")
    print("=" * 60)

    if not weather_info.get("success"):
        print(f"❌ Error: {weather_info.get('error')}")
        print("=" * 60)
        return

    city = weather_info["city"]
    country = f", {weather_info['country']}" if weather_info.get("country") else ""
    temp = weather_info["temperature"]
    unit = weather_info["unit"]
    apparent = weather_info.get("apparent_temperature")
    humidity = weather_info.get("humidity")
    wind = weather_info.get("wind_speed")
    wind_unit = weather_info.get("wind_unit", "km/h")
    desc = weather_info.get("weather_description")
    icon = weather_info.get("icon", "🌤️")
    ts = weather_info.get("timestamp", "N/A")
    lat = weather_info.get("latitude")
    lon = weather_info.get("longitude")

    print(f"📍 Location      : {city}{country} (Lat: {lat:.4f}, Lon: {lon:.4f})")
    print(f"🕒 Recorded Time : {ts}")
    print(f"🌡️  Temperature   : {temp} {unit}  ({icon} {desc})")
    if apparent is not None:
        print(f"🤔 Feels Like    : {apparent} {unit}")
    if humidity is not None:
        print(f"💧 Humidity      : {humidity}%")
    if wind is not None:
        print(f"💨 Wind Speed    : {wind} {wind_unit}")
    print("-" * 60)
    print(f"👉 Current Temperature in {city}: {temp} {unit}")
    print("=" * 60)


def main():
    """Main execution entry point."""
    target_city = sys.argv[1] if len(sys.argv) > 1 else "Ahmedabad"
    print(f"\n[Open-Meteo Agent] Fetching real-time weather for '{target_city}'...")
    weather_data = get_current_weather(target_city)
    display_weather_report(weather_data)


if __name__ == "__main__":
    main()
