# -------- MULTI-HOP REASONING AGENT --------

movie_year = {
    "Bahubali": 2015,
    "KGF": 2018,
    "Pushpa": 2021,
    "Dangal": 2016
}

top_song = {
    2015: "Gerua",
    2016: "Kar Gayi Chull",
    2018: "Apna Time Aayega",
    2021: "Srivalli"
}

def movie_song_agent(movie):

    if movie in movie_year:

        year = movie_year[movie]

        song = top_song.get(year, "No song available")

        print("Movie :", movie)
        print("Release Year :", year)
        print("Top Trending Song :", song)

    else:
        print("Movie not found.")


movie_name = input("Enter movie name: ")
movie_song_agent(movie_name)



# output:
# Enter movie name: Pushpa
# Movie : Pushpa
# Release Year : 2021
# Top Trending Song : Srivalli