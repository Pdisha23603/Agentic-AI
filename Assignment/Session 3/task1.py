# -------- PERCEIVE → THINK → ACT → LEARN --------

def food_agent():

    # PERCEIVE
    food = input("What food do you like? ").lower()

    # THINK
    restaurants = {
        "pizza": "Domino's Pizza",
        "burger": "McDonald's",
        "biryani": "Behrouz Biryani",
        "south indian": "Saravana Bhavan",
        "chinese": "Mainland China"
    }

    restaurant = restaurants.get(food, "Food Plaza Restaurant")

    # ACT
    print("\nSuggested Restaurant:", restaurant)

    # LEARN
    feedback = input("Did you like this suggestion? (yes/no): ").lower()

    if feedback == "yes":
        print("Great! I will remember this preference for better suggestions.")
    else:
        print("Thanks for your feedback. Next time I will suggest a different restaurant.")


# Run the agent
food_agent()



# output:
# PS C:\Users\disha\agentic ai\Tops task\Assignment\Session 3> & C:\Users\disha\AppData\Local\Programs\Python\Python314\python.exe "c:/Users/disha/agentic ai/Tops task/Assignment/Session 3/task1.py"
# What food do you like? pizza

# Suggested Restaurant: Domino's Pizza
# Did you like this suggestion? (yes/no): no
# Thanks for your feedback. Next time I will suggest a different restaurant.
# PS C:\Users\disha\agentic ai\Tops task\Assignment\Session 3> & C:\Users\disha\AppData\Local\Programs\Python\Python314\python.exe "c:/Users/disha/agentic ai/Tops task/Assignment/Session 3/task1.py"
# What food do you like? pizza

# Suggested Restaurant: Domino's Pizza
# Did you like this suggestion? (yes/no): yes
# Great! I will remember this preference for better suggestions.
# PS C:\Users\disha\agentic ai\Tops task\Assignment\Session 3> 

