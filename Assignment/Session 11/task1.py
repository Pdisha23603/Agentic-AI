# ============================================
# Task 1: Multi-Agent Food Delivery System
# ============================================

# Agent 1 - Fetch Menu
def fetch_menu():
    print("Agent 1: Fetching restaurant menu...")

    menu = [
        {"item": "Pizza", "price": 250},
        {"item": "Burger", "price": 150},
        {"item": "Pasta", "price": 220},
        {"item": "Cold Coffee", "price": 120}
    ]

    return menu


# Agent 2 - Analyze Customer Order
def analyze_orders(menu):
    print("Agent 2: Analyzing customer order...")

    ordered_items = ["Pizza", "Cold Coffee"]

    total_bill = 0

    for food in menu:
        if food["item"] in ordered_items:
            total_bill += food["price"]

    return {
        "ordered_items": ordered_items,
        "total_bill": total_bill
    }


# Agent 3 - Generate Delivery Report
def generate_delivery_report(order_summary):
    print("Agent 3: Generating delivery report...\n")

    print("===== FOOD DELIVERY REPORT =====")
    print("Ordered Items :", ", ".join(order_summary["ordered_items"]))
    print("Total Bill    : ₹", order_summary["total_bill"])
    print("Delivery      : Confirmed")
    print("Estimated Time: 30 Minutes")


# Multi-Agent Workflow
menu_data = fetch_menu()
order_data = analyze_orders(menu_data)
generate_delivery_report(order_data)