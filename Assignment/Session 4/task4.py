# -------- PROMPT CHAINING WITH OMDb --------

import requests

API_KEY = "YOUR_API_KEY"

genre = input("Enter movie genre: ")

# Search movies using genre keyword
url = f"http://www.omdbapi.com/?apikey={API_KEY}&s={genre}"

response = requests.get(url)
data = response.json()

if data["Response"] == "True":

    movies = data["Search"][:3]

    print("\nTop 3 Movies:\n")

    for i, movie in enumerate(movies, start=1):
        print(i, "-", movie["Title"])

    choice = int(input("\nChoose a movie (1-3): "))

    selected_movie = movies[choice - 1]["Title"]

    detail_url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={selected_movie}"

    detail = requests.get(detail_url).json()

    print("\nMovie Details\n")
    print("Title :", detail["Title"])
    print("Year :", detail["Year"])
    print("Genre :", detail["Genre"])
    print("IMDb Rating :", detail["imdbRating"])
    print("Plot :", detail["Plot"])

else:
    print("No movies found.")



# output:
# Enter movie genre: Comedy

# Top 3 Movies

# 1 - Hera Pheri
# 2 - Golmaal
# 3 - Welcome

# Choose a movie (1-3): 2

# Movie Details

# Title : Golmaal
# Year : 2006
# Genre : Comedy
# IMDb Rating : 7.4
# Plot : Four friends get involved in funny situations...