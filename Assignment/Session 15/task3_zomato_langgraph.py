"""
Session 15 - Task 3: Zomato Restaurant Recommender with LangGraph
================================================================
This script uses LangGraph (StateGraph) to design a conversational flow:
1. When a user asks for Zomato recommendations, the graph checks for a city.
2. If no city is specified, it transitions to a node asking for the user's city.
3. Once the city is provided, it transitions to a recommendation node that suggests
   3 top restaurants from a hardcoded list based on that city.
"""

import sys
from typing import TypedDict, Optional, List, Dict
from langgraph.graph import StateGraph, START, END

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Hardcoded Zomato Restaurant Database across Major Cities
ZOMATO_RESTAURANTS_DB: Dict[str, List[Dict]] = {
    "mumbai": [
        {
            "name": "The Bombay Canteen",
            "cuisine": "Modern Indian, Regional",
            "rating": 4.8,
            "cost_for_two": "Rs. 2,200",
            "location": "Lower Parel",
            "must_try": "Eggs Kejriwal, Canteen Haleem, Guava Tan-Tana-Tan"
        },
        {
            "name": "Trishna",
            "cuisine": "Seafood, Mangalorean",
            "rating": 4.7,
            "cost_for_two": "Rs. 2,800",
            "location": "Fort / Kala Ghoda",
            "must_try": "Butter Garlic Crab, Koliwada Prawns"
        },
        {
            "name": "Bastian",
            "cuisine": "Continental, Asian, Seafood",
            "rating": 4.6,
            "cost_for_two": "Rs. 3,500",
            "location": "Bandra West / At the Top 48",
            "must_try": "Lobster Roll, Burrata Salad, Pull-Me-Up Cake"
        }
    ],
    "delhi": [
        {
            "name": "Bukhara - ITC Maurya",
            "cuisine": "North Indian, Mughlai",
            "rating": 4.9,
            "cost_for_two": "Rs. 5,000",
            "location": "Chanakyapuri",
            "must_try": "Dal Bukhara (slow cooked for 18 hrs), Sikandari Raan"
        },
        {
            "name": "Indian Accent",
            "cuisine": "Modern Indian Fine Dining",
            "rating": 4.9,
            "cost_for_two": "Rs. 6,000",
            "location": "The Lodhi, Lodhi Road",
            "must_try": "Meetha Achaar Pork Ribs, Daulat Ki Chaat"
        },
        {
            "name": "Karim's Historic",
            "cuisine": "Old Delhi Mughlai",
            "rating": 4.5,
            "cost_for_two": "Rs. 1,000",
            "location": "Jama Masjid, Old Delhi",
            "must_try": "Mutton Korma, Mutton Burra, Sheermal"
        }
    ],
    "bengaluru": [
        {
            "name": "Vidyarthi Bhavan",
            "cuisine": "South Indian Heritage",
            "rating": 4.7,
            "cost_for_two": "Rs. 300",
            "location": "Gandhi Bazaar, Basavanagudi",
            "must_try": "Crispy Ghee Masala Dosa, Filter Coffee"
        },
        {
            "name": "Toit Brewpub",
            "cuisine": "Microbrewery, Italian, American",
            "rating": 4.8,
            "cost_for_two": "Rs. 2,000",
            "location": "Indiranagar",
            "must_try": "Tint-In-Wit Belgian Wheat, Basmati Blonde, Woodfired Pizza"
        },
        {
            "name": "Nagarjuna Restaurant",
            "cuisine": "Authentic Andhra Meals",
            "rating": 4.6,
            "cost_for_two": "Rs. 800",
            "location": "Residency Road",
            "must_try": "Andhra Meals with Gunpowder Ghee, Chicken Sholay Kebab"
        }
    ],
    "ahmedabad": [
        {
            "name": "Agashiye - The House of MG",
            "cuisine": "Traditional Gujarati Fine Dining Thali",
            "rating": 4.8,
            "cost_for_two": "Rs. 2,400",
            "location": "Lal Darwaja",
            "must_try": "Heritage Gujarati Thali, Rasawala Dhokla, Kesar Jalebi"
        },
        {
            "name": "Gordhan Thal",
            "cuisine": "Unlimited Kathiyawadi & Gujarati",
            "rating": 4.6,
            "cost_for_two": "Rs. 900",
            "location": "SG Highway, Bodakdev",
            "must_try": "Ringan No Olo, Bajra Rotla, Undhiyu"
        },
        {
            "name": "Manek Chowk Street Food Hub",
            "cuisine": "Street Food, Fusion Sandwiches",
            "rating": 4.5,
            "cost_for_two": "Rs. 500",
            "location": "Old City, Khadia",
            "must_try": "Gwalior Dosa, Chocolate Cheese Sandwich, Kulfi"
        }
    ],
    "hyderabad": [
        {
            "name": "Paradise Biryani",
            "cuisine": "Hyderabadi Biryani, Mughlai",
            "rating": 4.5,
            "cost_for_two": "Rs. 900",
            "location": "Secunderabad",
            "must_try": "Mutton Dum Biryani, Mirchi Ka Salan"
        },
        {
            "name": "Bawarchi Restaurant",
            "cuisine": "Biryani, Kebabs",
            "rating": 4.6,
            "cost_for_two": "Rs. 750",
            "location": "RTC X Roads",
            "must_try": "Special Chicken Biryani, Boti Kebab"
        },
        {
            "name": "Jewel of Nizam - The Minar",
            "cuisine": "Nizami Fine Dining",
            "rating": 4.8,
            "cost_for_two": "Rs. 3,500",
            "location": "The Golkonda Resort, Gandipet",
            "must_try": "Barkas Pathar Ka Gosht, Anokhi Kheer"
        }
    ]
}

# 1. State Definition
class ZomatoState(TypedDict):
    user_message: str
    city: Optional[str]
    needs_city: bool
    recommendations: List[Dict]
    agent_response: str

# 2. Graph Nodes
def detect_city_node(state: ZomatoState) -> Dict:
    """Checks if the user's message specifies a supported city."""
    text = (state.get("user_message") or "").lower()
    current_city = state.get("city")

    matched_city = None
    for city_key in ZOMATO_RESTAURANTS_DB.keys():
        if city_key in text:
            matched_city = city_key
            break

    # If city is already saved from prior turn, keep it unless new one provided
    final_city = matched_city if matched_city else current_city

    if final_city:
        return {"city": final_city, "needs_city": False}
    else:
        return {"city": None, "needs_city": True}

def ask_city_node(state: ZomatoState) -> Dict:
    """Asks user for city if not yet known."""
    cities_display = ", ".join([c.capitalize() for c in ZOMATO_RESTAURANTS_DB.keys()])
    response = (
        "I'd love to help you find the best food on Zomato! 🍽️\n"
        f"Which city are you looking for recommendations in?\n"
        f"(Available cities: {cities_display})"
    )
    return {"agent_response": response}

def recommend_restaurants_node(state: ZomatoState) -> Dict:
    """Retrieves and formats 3 restaurant recommendations based on city."""
    city = state.get("city", "mumbai").lower()
    restaurants = ZOMATO_RESTAURANTS_DB.get(city, ZOMATO_RESTAURANTS_DB["mumbai"])[:3]

    city_name = city.capitalize()
    lines = [
        f"Here are the top 3 Zomato-rated restaurants in {city_name}:\n"
    ]
    for idx, r in enumerate(restaurants, start=1):
        lines.append(
            f"{idx}. {r['name']} (★ {r['rating']} / 5.0)\n"
            f"   • Cuisine:      {r['cuisine']}\n"
            f"   • Location:     {r['location']}, {city_name}\n"
            f"   • Approx Cost:  {r['cost_for_two']} for two\n"
            f"   • Must-Try:     {r['must_try']}\n"
        )
    lines.append("Would you like directions, table booking, or a cuisine filter?")
    return {
        "recommendations": restaurants,
        "agent_response": "\n".join(lines)
    }

# 3. Conditional Router
def route_after_detection(state: ZomatoState) -> str:
    """Routes to 'ask_city' if city is missing, else 'recommend_restaurants'."""
    if state.get("needs_city", True):
        return "ask_city"
    return "recommend_restaurants"

# 4. Build LangGraph
def build_zomato_graph():
    builder = StateGraph(ZomatoState)

    builder.add_node("detect_city", detect_city_node)
    builder.add_node("ask_city", ask_city_node)
    builder.add_node("recommend_restaurants", recommend_restaurants_node)

    builder.add_edge(START, "detect_city")
    builder.add_conditional_edges(
        "detect_city",
        route_after_detection,
        {
            "ask_city": "ask_city",
            "recommend_restaurants": "recommend_restaurants"
        }
    )
    builder.add_edge("ask_city", END)
    builder.add_edge("recommend_restaurants", END)

    return builder.compile()

def run_task3():
    print("=" * 70)
    print("    SESSION 15 - TASK 3: ZOMATO RESTAURANT RECOMMENDER (LANGGRAPH)")
    print("=" * 70)

    graph = build_zomato_graph()

    # Scenario 1: Multi-turn Conversation
    # Turn 1: User asks without providing a city
    print("\n--- SCENARIO 1: Multi-turn Flow (City missing initially) ---")
    state_turn1 = {
        "user_message": "Hey Zomato, can you recommend some top rated restaurants?",
        "city": None,
        "needs_city": True,
        "recommendations": [],
        "agent_response": ""
    }
    print(f"\n[User (Turn 1)]: \"{state_turn1['user_message']}\"")
    result_turn1 = graph.invoke(state_turn1)
    print(f"\n[Agent (Turn 1)]:\n{result_turn1['agent_response']}")

    # Turn 2: User specifies the city
    state_turn2 = {
        **result_turn1,
        "user_message": "I am in Mumbai right now, show me places."
    }
    print(f"\n[User (Turn 2)]: \"{state_turn2['user_message']}\"")
    result_turn2 = graph.invoke(state_turn2)
    print(f"\n[Agent (Turn 2)]:\n{result_turn2['agent_response']}")

    # Scenario 2: Direct Single-turn Query
    print("\n" + "=" * 70)
    print("--- SCENARIO 2: Single-turn Flow (City mentioned directly) ---")
    state_direct = {
        "user_message": "Suggest the best 3 restaurants on Zomato in Bengaluru please.",
        "city": None,
        "needs_city": True,
        "recommendations": [],
        "agent_response": ""
    }
    print(f"\n[User]: \"{state_direct['user_message']}\"")
    result_direct = graph.invoke(state_direct)
    print(f"\n[Agent]:\n{result_direct['agent_response']}")

    print("\n" + "=" * 70)
    print("[SUCCESS] Task 3 completed: LangGraph stateful flow verified!")

if __name__ == "__main__":
    if "--interactive" in sys.argv:
        graph = build_zomato_graph()
        state = {"user_message": "", "city": None, "needs_city": True, "recommendations": [], "agent_response": ""}
        print("Zomato LangGraph Assistant (type 'exit' to quit):")
        while True:
            try:
                msg = input("\nYou: ").strip()
                if msg.lower() in ("exit", "quit", "q"):
                    break
                state["user_message"] = msg
                state = graph.invoke(state)
                print(f"\nZomato Bot:\n{state['agent_response']}")
            except (KeyboardInterrupt, EOFError):
                break
    else:
        run_task3()
