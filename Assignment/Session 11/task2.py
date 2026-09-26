# ============================================
# Task 2: Cooperative Spotify Agents
# ============================================

# Agent 1 - Fetch Trending Songs
def fetch_trending_songs():
    print("Agent 1: Fetching trending Spotify songs...\n")

    songs = [
        {"title": "Blinding Lights", "genre": "Pop"},
        {"title": "Levitating", "genre": "Pop"},
        {"title": "Believer", "genre": "Rock"},
        {"title": "Perfect", "genre": "Pop"},
        {"title": "Shape of You", "genre": "Pop"},
        {"title": "Apna Bana Le", "genre": "Romantic"}
    ]

    return songs


# Agent 2 - Analyze Pop Songs
def analyze_pop_songs(song_list):
    print("Agent 2: Counting Pop genre songs...\n")

    pop_count = 0

    for song in song_list:
        if song["genre"] == "Pop":
            pop_count += 1

    return pop_count


# Multi-Agent Workflow
playlist = fetch_trending_songs()
total_pop = analyze_pop_songs(playlist)

print("===== SPOTIFY REPORT =====")
print("Total Songs :", len(playlist))
print("Pop Songs   :", total_pop)