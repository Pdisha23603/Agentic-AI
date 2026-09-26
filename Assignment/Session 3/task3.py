# -------- LONG-TERM MEMORY PLAYLIST --------

filename = "playlist_history.txt"

# Add a new song
song = input("Enter song name: ")

with open(filename, "a") as file:
    file.write(song + "\n")

print("\nSong saved successfully!")

# Display full history
print("\nYour Complete Play History:")

with open(filename, "r") as file:
    history = file.readlines()

for number, song in enumerate(history, start=1):
    print(number, "-", song.strip())



# output:
# Enter song name: Kesariya

# Song saved successfully!

# Your Complete Play History:
# 1 - Believer
# 2 - Shape of You
# 3 - Kesariya