import sqlite3

connection = sqlite3.connect("music.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS songs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_name TEXT
)
""")

cursor.execute("INSERT INTO songs(song_name) VALUES ('Believer')")
cursor.execute("INSERT INTO songs(song_name) VALUES ('Kesariya')")
cursor.execute("INSERT INTO songs(song_name) VALUES ('Shape of You')")

connection.commit()
connection.close()



