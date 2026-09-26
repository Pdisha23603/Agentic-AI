# ============================================
# Task 4: Agent-to-Agent Communication
# ============================================

# Agent 1
def fetch_restaurant_data():
    print("Agent 1: Fetching restaurant data...")

    restaurants = [
        {"name": "Domino's", "rating": 4.3},
        {"name": "Barbeque Nation", "rating": 4.7},
        {"name": "Pizza Hut", "rating": 4.2}
    ]

    return restaurants


# Agent 2
def analyze_restaurant_data(restaurants):
    print("Agent 2: Finding highest-rated restaurant...")

    best_restaurant = max(restaurants, key=lambda restaurant: restaurant["rating"])

    return best_restaurant


# Agent 3
def display_restaurant_report(best_restaurant):
    print("\n===== RESTAURANT REPORT =====")
    print("Best Restaurant :", best_restaurant["name"])
    print("Rating          :", best_restaurant["rating"])


# Agent-to-Agent Workflow
restaurant_data = fetch_restaurant_data()
best_data = analyze_restaurant_data(restaurant_data)
display_restaurant_report(best_data)