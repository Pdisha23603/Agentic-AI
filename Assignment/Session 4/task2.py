# -------- ZOMATO MENU SEARCH --------

import pandas as pd

# Read CSV file
menu = pd.read_csv("menu.csv")

# User Input
cuisine = input("Enter cuisine type: ")

# Filter matching dishes
result = menu[menu["cuisine"].str.lower() == cuisine.lower()]

if len(result) > 0:
    print("\nAvailable Dishes:\n")

    for index, row in result.iterrows():
        print(f"{row['dish']} - ₹{row['price']}")

else:
    print("No dishes found for this cuisine.")




# output:
# Enter cuisine type: Italian

# Available Dishes:

# Margherita Pizza - ₹250
# Pasta Alfredo - ₹320