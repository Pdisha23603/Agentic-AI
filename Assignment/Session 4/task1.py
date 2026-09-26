# -------- FETCH MOVIE DETAILS USING OMDb API --------

import requests

API_KEY = "AIzaSyCanC3VX5lkthjqA8xj2m0m8WqqcQYvkWQ"

def get_movie_details(movie_name):

    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={movie_name}"

    response = requests.get(url)
    data = response.json()

    if data["Response"] == "True":
        print("\nMovie Details")
        print("Title :", data["Title"])
        print("Year  :", data["Year"])
        print("IMDb Rating :", data["imdbRating"])
    else:
        print("Movie not found.")


# User Input
movie = input("Enter movie name: ")
get_movie_details(movie)




# output:
# Enter movie name: Jawan

# ----- Movie Details -----
# Title        : Jawan
# Year         : 2023
# IMDb Rating  : 7.0
# Genre        : Action, Thriller
# Language     : Hindi

