{
  "name": "movieTicketFinder",
  "description": "Finds available movie tickets based on city, movie name, and date.",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "City where the user wants to watch the movie."
      },
      "movie_name": {
        "type": "string",
        "description": "Name of the movie."
      },
      "date": {
        "type": "string",
        "description": "Date of the movie in YYYY-MM-DD format."
      }
    },
    "required": ["city", "movie_name", "date"]
  }
}