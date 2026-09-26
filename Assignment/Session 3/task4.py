# -------- CONTEXTUAL MEMORY MOVIE AGENT --------

last_watched = {
    "title": "Bhool Bhulaiyaa 2",
    "genre": "Comedy"
}

comedy_movies = [
    "Hera Pheri",
    "Golmaal",
    "Fukrey",
    "Housefull",
    "Welcome"
]

query = input("Ask for a movie recommendation: ").lower()

if "comedy" in query:
    print("\nLast watched movie:", last_watched["title"])
    print("Genre:", last_watched["genre"])

    print("\nComedy movies you may like:")
    for movie in comedy_movies:
        print("-", movie)
else:
    print("Please ask for comedy movie recommendations.")




# output:
# Ask for a movie recommendation:
# comedy movies like the one I watched last week

# Last watched movie: Bhool Bhulaiyaa 2
# Genre: Comedy

# Comedy movies you may like:
# - Hera Pheri
# - Golmaal
# - Fukrey
# - Housefull
# - Welcome