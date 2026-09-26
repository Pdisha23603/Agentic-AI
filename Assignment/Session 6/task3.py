{
  "type": "function",
  "function": {
    "name": "getWeather",
    "description": "Gets the weather forecast for a given location and date.",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "City or location for weather information."
        },
        "date": {
          "type": "string",
          "description": "Date for the weather forecast in YYYY-MM-DD format."
        }
      },
      "required": ["location", "date"]
    }
  }
}