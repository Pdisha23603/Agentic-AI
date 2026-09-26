# ============================================
# Task 3: Spotify Playlist Decision Agent
# ============================================

def decide_playlist_action(song_likes, song_skips):
    """
    Decide whether to Recommend, Remove, or Promote a song.
    """

    if song_likes >= 100 and song_skips <= 20:
        return "Promote Song"

    elif song_skips > song_likes:
        return "Remove Song"

    else:
        return "Recommend Song"


# Test Examples
print("Song 1:", decide_playlist_action(120, 10))
print("Song 2:", decide_playlist_action(25, 50))
print("Song 3:", decide_playlist_action(60, 30))