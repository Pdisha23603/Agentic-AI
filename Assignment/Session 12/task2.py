# ============================================
# Task 2: Zomato Food Ordering Agent Plan
# ============================================

# Step 1: Recommend Restaurant
def recommend_restaurant(location):
    print("Step 1: Searching restaurants in", location)
    return "Barbeque Nation"


# Step 2: Show Menu
def show_menu(restaurant):
    print("Step 2: Showing menu for", restaurant)

    menu = ["Pizza", "Burger", "Pasta", "Biryani"]
    return menu


# Step 3: Place Order
def place_order(food_item):
    print("Step 3: Placing order for", food_item)

    return {
        "order_status": "Order Placed",
        "item": food_item
    }


# Step 4: Confirm Delivery
def confirm_delivery(order):
    print("Step 4: Confirming delivery")

    print("Order Item :", order["item"])
    print("Status     :", order["order_status"])
    print("Delivery   : Expected in 30 minutes")


# Agent Workflow
restaurant = recommend_restaurant("Ahmedabad")

menu = show_menu(restaurant)

order = place_order(menu[0])

confirm_delivery(order)