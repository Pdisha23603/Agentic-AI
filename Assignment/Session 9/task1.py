# ============================================
# Task 1: Food Delivery Chatbot Agent
# ============================================

def food_delivery_agent(user_input):
    """
    Simulates a food delivery agent using
    high-level planning and external actions.
    """

    print("=== Food Delivery AI Agent ===")

    # High-level planning (safe simulation)
    print("[Planning] Analyzing user request...")

    user_input = user_input.lower()

    if "restaurant" in user_input or "recommend" in user_input:
        print("[Planning] User wants a restaurant recommendation.")
        print("[Action] Suggested Restaurant: Barbeque Nation")

    elif "menu" in user_input:
        print("[Planning] User wants to view the menu.")
        print("[Action] Menu: Pizza, Burger, Pasta, Sandwich, Cold Coffee")

    elif "order" in user_input or "confirm" in user_input:
        print("[Planning] User wants to confirm an order.")
        print("[Action] Your food order has been confirmed.")

    else:
        print("[Planning] Request is unclear.")
        print("[Action] Please tell me if you want a restaurant, menu, or order confirmation.")


# Example Calls
food_delivery_agent("Recommend a restaurant")
print()

food_delivery_agent("Show me the menu")
print()

food_delivery_agent("Confirm my order")