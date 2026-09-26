# ============================================
# Task 3: Spotify Song Information
# ============================================

import requests


ACCESS_TOKEN = "YOUR_SPOTIFY_ACCESS_TOKEN"


def fetch_song_info(song_name):
    """
    Fetch artist and album name from Spotify API.
    """

    url = "https://api.spotify.com/v1/search"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "q": song_name,
        "type": "track",
        "limit": 1
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "tracks" in data and data["tracks"]["items"]:

        track = data["tracks"]["items"][0]

        print("===== Spotify Song Information =====")
        print("Song   :", track["name"])
        print("Artist :", track["artists"][0]["name"])
        print("Album  :", track["album"]["name"])

    else:
        print("Song not found.")


# Example
fetch_song_info("Perfect")