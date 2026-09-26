# -------- SWIGGY FOOD ORDERING AGENT --------

restaurants = {
    "Dominos": {
        "Pizza": 250,
        "Garlic Bread": 120,
        "Coke": 50
    },
    "McDonalds": {
        "Burger": 180,
        "Fries": 90,
        "Cold Coffee": 110
    }
}

# Step 1: Select Restaurant
print("Available Restaurants:")
for restaurant in restaurants:
    print("-", restaurant)

selected_restaurant = input("\nSelect Restaurant: ")

# Safety Check
if selected_restaurant not in restaurants:
    print("Restaurant not available.")
else:

    menu = restaurants[selected_restaurant]

    print("\nMenu:")
    for dish, price in menu.items():
        print(f"{dish} - ₹{price}")

    # Step 2: Choose Dishes
    selected_dish = input("\nChoose Dish: ")

    # Safety Check
    if selected_dish not in menu:
        print("Dish not available in selected restaurant.")

    else:
        quantity = int(input("Enter Quantity: "))

        # Step 3: Calculate Total
        total = menu[selected_dish] * quantity

        print("\nOrder Summary")
        print("Restaurant:", selected_restaurant)
        print("Dish:", selected_dish)
        print("Quantity:", quantity)
        print("Total Price: ₹", total)

        # Step 4: Confirm Order
        confirm = input("Confirm Order? (yes/no): ").lower()

        if confirm == "yes":
            print("Order Confirmed. Your food is being prepared.")
        else:
            print("Order Cancelled.")





# output
# Available Restaurants:
# - Dominos
# - McDonalds

# Select Restaurant: Dominos

# Menu:
# Pizza - ₹250
# Garlic Bread - ₹120
# Coke - ₹50

# Choose Dish: Pizza
# Enter Quantity: 2

# Order Summary
# Restaurant: Dominos
# Dish: Pizza
# Quantity: 2
# Total Price: ₹500

# Confirm Order? yes

# Order Confirmed. Your food is being prepared.