def decide_next_action(perceived_data):
    intent = perceived_data["intent"]
    apps = perceived_data["apps"]
    keywords = perceived_data["keywords"]

    # Spotify action
    if "spotify" in apps and "trending" in keywords:
        return "fetch_spotify_trending"

    # BookMyShow action
    elif "bookmyshow" in apps and intent in ["book", "search"]:
        return "search_movie_bookmyshow"

    # YouTube action
    elif "youtube" in apps and intent == "play":
        return "play_youtube_video"

    # Zomato action
    elif "zomato" in apps:
        return "search_restaurants"

    # Swiggy action
    elif "swiggy" in apps:
        return "order_food"

    # Default action
    else:
        return "unknown_action"


# Example input (perceived data)
result = {
    "intent": "show",
    "apps": ["spotify"],
    "keywords": ["trending", "songs"]
}

# Call the function
action = decide_next_action(result)

# Print output
print("Next Action:", action)





# output:
# Next Action: fetch_spotify_trending