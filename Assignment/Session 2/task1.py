import re

def perceive_input(user_message):
    # Convert text to lowercase
    text = user_message.lower()

    # Intent words
    intent_words = ["show", "play", "book", "search", "find"]

    # App names
    apps = ["spotify", "youtube", "bookmyshow", "zomato", "swiggy"]

    # Find intent
    intent = "unknown"
    for word in intent_words:
        if word in text:
            intent = word
            break

    # Find app names
    found_apps = []
    for app in apps:
        if app in text:
            found_apps.append(app)

    # Extract keywords (only letters)
    keywords = re.findall(r"[a-zA-Z]+", text)

    # Return structured dictionary
    return {
        "intent": intent,
        "apps": found_apps,
        "keywords": keywords
    }


# Example
message = "Show me trending songs on Spotify"
result = perceive_input(message)

print(result)



# output:
# {'intent': 'show', 'apps': ['spotify'], 'keywords': ['show', 'me', 'trending', 'songs', 'on', 'spotify']}
