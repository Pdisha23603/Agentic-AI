# ============================================
# Task 3: Weather Advisory Function
# ============================================

def weather_advisory(temp_celsius):
    """
    Returns an advisory message based on temperature.
    """

    if temp_celsius < 20:
        return "Carry an umbrella ☔"

    elif temp_celsius > 30:
        return "Stay hydrated 💧"

    else:
        return "Weather is pleasant 😊"


# Example
print(weather_advisory(18))
print(weather_advisory(32))
print(weather_advisory(25))