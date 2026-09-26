# ============================================
# Task 2: Simple Spotify Agent
# File: spotify_agent.py
# ============================================

def spotify_agent(user_input):
    user_input = user_input.lower()

    if "trending" in user_input and "song" in user_input:
        return "Fetching trending songs from Spotify."

    elif "playlist" in user_input:
        return "Opening your Spotify playlist."

    elif "artist" in user_input:
        return "Searching for the requested artist."

    else:
        return "Please ask about songs, playlists, or artists."


print("====== Spotify AI Agent ======")

query = input("Enter your request: ")

response = spotify_agent(query)

print("Agent Response:", response)