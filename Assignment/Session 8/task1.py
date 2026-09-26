# ============================================
# Task 1: Mock Weather Function
# ============================================

def get_weather(city_name):
    """
    Returns a mock weather temperature for a city.
    """

    temperature = 28  # Mock temperature

    print("Weather Report")
    print("-" * 30)
    print(f"City        : {city_name}")
    print(f"Temperature : {temperature}°C")


# Example
get_weather("Ahmedabad")