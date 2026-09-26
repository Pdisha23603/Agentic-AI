import re

# ---------------- PERCEIVE ----------------
def perceive_input(user_message):
    text = user_message.lower()

    intent_words = ["show", "play", "book", "search", "find"]
    apps = ["spotify", "youtube", "bookmyshow", "zomato", "swiggy"]

    intent = "unknown"
    for word in intent_words:
        if word in text:
            intent = word
            break

    found_apps = []
    for app in apps:
        if app in text:
            found_apps.append(app)

    keywords = re.findall(r"[a-zA-Z]+", text)

    return {
        "intent": intent,
        "apps": found_apps,
        "keywords": keywords
    }


# ---------------- THINK ----------------
def decide_next_action(perceived_data):
    intent = perceived_data["intent"]
    apps = perceived_data["apps"]
    keywords = perceived_data["keywords"]

    if "spotify" in apps and "trending" in keywords:
        return "fetch_spotify_trending"

    elif "bookmyshow" in apps and intent in ["book", "search"]:
        return "search_movie_bookmyshow"

    elif "youtube" in apps and intent == "play":
        return "play_youtube_video"

    elif "zomato" in apps:
        return "search_restaurants"

    elif "swiggy" in apps:
        return "order_food"

    else:
        return "unknown_action"


# ---------------- ACT ----------------
def execute_action(action):

    if action == "fetch_spotify_trending":
        print("Fetching trending songs from Spotify...")

    elif action == "search_movie_bookmyshow":
        print("Searching movies on BookMyShow...")

    elif action == "play_youtube_video":
        print("Playing video on YouTube...")

    elif action == "search_restaurants":
        print("Searching restaurants on Zomato...")

    elif action == "order_food":
        print("Ordering food from Swiggy...")

    else:
        print("Sorry! I don't understand the request.")


# ---------------- MAIN LOOP ----------------
user_message = input("Enter your request: ")

perceived = perceive_input(user_message)
print("Perceived Data:", perceived)

action = decide_next_action(perceived)
print("Next Action:", action)

execute_action(action)





# output:
# Enter your request: Show me trending songs on Spotify
# Perceived Data: {'intent': 'show', 'apps': ['spotify'], 'keywords': ['show', 'me', 'trending', 'songs', 'on', 'spotify']}
# Next Action: fetch_spotify_trending
# Fetching trending songs from Spotify...



