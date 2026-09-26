{
  "name": "songSearch",
  "description": "Searches for songs in a Spotify-style music application using song name and artist name.",
  "parameters": {
    "type": "object",
    "properties": {
      "song_name": {
        "type": "string",
        "description": "Name of the song to search."
      },
      "artist": {
        "type": "string",
        "description": "Name of the artist who sings the song."
      }
    },
    "required": ["song_name", "artist"]
  }
}