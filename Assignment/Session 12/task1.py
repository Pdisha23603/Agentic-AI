# ============================================
# Task 1: Weather API Tool for LLM Agent
# ============================================

# Mock Weather API Tool
def call_weather_api(city_name):
    """
    Returns fake weather information for a city.
    """

    weather_data = {
        "Ahmedabad": 33,
        "Mumbai": 29,
        "Delhi": 35,
        "Bengaluru": 25,
        "Pune": 27
    }

    temperature = weather_data.get(city_name, 28)

    return {
        "city": city_name,
        "temperature": temperature,
        "unit": "°C"
    }


# LLM Agent using the tool
def weather_agent(user_city):

    print("=== Weather AI Agent ===")
    print("Agent: Calling weather tool...\n")

    result = call_weather_api(user_city)

    print(f"City        : {result['city']}")
    print(f"Temperature : {result['temperature']}{result['unit']}")


# Example
weather_agent("Ahmedabad")