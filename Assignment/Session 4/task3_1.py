# -------- SONG SEARCH AGENT --------

import sqlite3

connection = sqlite3.connect("music.db")
cursor = connection.cursor()

song = input("Enter song name: ")

cursor.execute(
    "SELECT * FROM songs WHERE song_name = ?",
    (song,)
)

result = cursor.fetchone()

if result:
    print("Song found.")
else:
    print("Song not found.")

connection.close()


# output
# Enter song name: Kesariya

# Song found.
