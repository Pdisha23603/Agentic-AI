from fastmcp import FastMCP
import random

mcp = FastMCP("Spotify Recommendation MCP Server")

# ---------------------------------
# Static Tool
# ---------------------------------
@mcp.tool()
def hello_server():
    return {
        "message": "Welcome to Spotify MCP Server!"
    }


# ---------------------------------
# Song Recommendation Tool
# ---------------------------------
TRENDING_SONGS = [
    "APT - ROSÉ & Bruno Mars",
    "Die With A Smile - Lady Gaga & Bruno Mars",
    "Espresso - Sabrina Carpenter",
    "Birds of a Feather - Billie Eilish",
    "Beautiful Things - Benson Boone",
    "Ordinary - Alex Warren",
    "Shaky - Sanju Rathod",
    "Sapphire - Ed Sheeran",
    "Tauba Tauba - Karan Aujla",
    "Golden - Jung Kook"
]

@mcp.tool()
def get_song_recommendation():
    """
    Returns a random trending song.
    """

    song = random.choice(TRENDING_SONGS)

    return {
        "app": "Spotify",
        "recommendation": song,
        "category": "Trending Songs"
    }


# ---------------------------------
# Run HTTP Server
# ---------------------------------
if __name__ == "__main__":
    print("Spotify MCP Server Running...")
    mcp.run(transport="http", host="127.0.0.1", port=8000)