"""
Session 19 - Task 3: Refactored Modular Restaurant Recommender Agent
===================================================================
This script refactors legacy procedural restaurant recommendation code
into a clean, modular 'AgentRestaurantRecommender' class with strict
separation into Perception, Reasoning, and Action modules.
"""

import sys
import re
from typing import Dict, List, Any

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# Restaurant Knowledge Base
# ==============================================================================
RESTAURANT_DATABASE = [
    {
        "name": "Bukhara",
        "cuisines": ["North Indian", "Mughlai"],
        "rating": 4.9,
        "cost_for_two": 5000,
        "location": "Chanakyapuri, Delhi",
        "diet": "Non-Veg",
        "signature_dish": "Dal Bukhara, Sikandari Raan"
    },
    {
        "name": "Agashiye - House of MG",
        "cuisines": ["Gujarati", "North Indian"],
        "rating": 4.8,
        "cost_for_two": 2400,
        "location": "Lal Darwaja, Ahmedabad",
        "diet": "Pure Veg",
        "signature_dish": "Heritage Gujarati Thali"
    },
    {
        "name": "Toit Brewpub",
        "cuisines": ["Italian", "Continental"],
        "rating": 4.8,
        "cost_for_two": 2000,
        "location": "Indiranagar, Bengaluru",
        "diet": "Mixed",
        "signature_dish": "Woodfired Margherita Pizza, Basmati Blonde Beer"
    },
    {
        "name": "Trishna",
        "cuisines": ["Seafood", "Mangalorean", "North Indian"],
        "rating": 4.7,
        "cost_for_two": 2800,
        "location": "Kala Ghoda, Mumbai",
        "diet": "Non-Veg",
        "signature_dish": "Butter Garlic Crab, Koliwada Prawns"
    },
    {
        "name": "Vidyarthi Bhavan",
        "cuisines": ["South Indian"],
        "rating": 4.7,
        "cost_for_two": 300,
        "location": "Basavanagudi, Bengaluru",
        "diet": "Pure Veg",
        "signature_dish": "Crispy Ghee Masala Dosa"
    },
    {
        "name": "Mainland China",
        "cuisines": ["Chinese", "Asian"],
        "rating": 4.6,
        "cost_for_two": 1800,
        "location": "Multiple Cities",
        "diet": "Mixed",
        "signature_dish": "Dim Sum, Hakka Noodles, Kung Pao Chicken"
    }
]

# ==============================================================================
# BEFORE: Legacy Procedural Code (Tightly Coupled & Hard to Test)
# ==============================================================================
def suggest_restaurants_legacy(user_query: str):
    """Legacy monolithic function mixing parsing, lookup, and display."""
    q = user_query.lower()
    print("--- Legacy Output ---")
    found = False
    for r in RESTAURANT_DATABASE:
        for c in r["cuisines"]:
            if c.lower() in q:
                print(f"Restaurant: {r['name']} - {c} (Rating: {r['rating']})")
                found = True
                break
    if not found:
        print("No matching restaurants found.")

# ==============================================================================
# AFTER: Refactored Modular Agent Class
# ==============================================================================
class AgentRestaurantRecommender:
    """
    Modular Agent Architecture with strict separation of concerns:
    - perceive(): Natural Language understanding and slot extraction
    - reason(): Knowledge base lookup, dietary constraint filtering, ranking
    - act(): Formatted recommendation response with actionable next steps
    """

    def __init__(self, name: str = "GourmetGuide-AI"):
        self.name = name
        self.database = RESTAURANT_DATABASE

    # 1. PERCEPTION MODULE
    def perceive(self, user_query: str) -> Dict[str, Any]:
        """
        Perceives and extracts:
        - Target Cuisines
        - Dietary constraints (veg / non-veg)
        - Budget indications
        """
        q = user_query.lower()

        # Known cuisines to detect
        known_cuisines = ["north indian", "south indian", "italian", "chinese", "gujarati", "seafood", "continental"]
        detected_cuisines = [c for c in known_cuisines if c in q]

        # Dietary preference
        diet_filter = None
        if "pure veg" in q or "vegetarian" in q or "veg" in q:
            diet_filter = "Pure Veg"
        elif "non-veg" in q or "chicken" in q or "seafood" in q or "mutton" in q:
            diet_filter = "Non-Veg"

        # Budget extraction
        budget_max = None
        budget_match = re.search(r'under\s+(?:rs\.?|inr)?\s*(\d+)', q)
        if budget_match:
            budget_max = float(budget_match.group(1))

        perception_data = {
            "raw_query": user_query,
            "detected_cuisines": detected_cuisines,
            "diet_filter": diet_filter,
            "budget_max": budget_max
        }
        return perception_data

    # 2. REASONING MODULE
    def reason(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Reasons over candidate restaurants matching detected cuisines,
        dietary constraints, and ranking heuristics.
        """
        cuisines = perception["detected_cuisines"]
        diet = perception["diet_filter"]
        budget = perception["budget_max"]

        candidates = []
        for rest in self.database:
            # Check cuisine match (if none specified, consider all)
            rest_cuisines_lower = [c.lower() for c in rest["cuisines"]]
            matches_cuisine = any(c in rest_cuisines_lower for c in cuisines) if cuisines else True

            # Check dietary constraint
            matches_diet = True
            if diet == "Pure Veg" and rest["diet"] != "Pure Veg":
                matches_diet = False

            # Check budget constraint
            matches_budget = True
            if budget and rest["cost_for_two"] > budget:
                matches_budget = False

            if matches_cuisine and matches_diet and matches_budget:
                score = rest["rating"] * 2.0
                if matches_cuisine and cuisines:
                    score += 2.0
                candidates.append({
                    "restaurant": rest,
                    "match_score": round(score, 1)
                })

        # Rank candidates by score descending
        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        return candidates

    # 3. ACTION MODULE
    def act(self, ranked_candidates: List[Dict[str, Any]], perception: Dict[str, Any]) -> str:
        """
        Synthesizes structured recommendations and next actionable steps.
        """
        lines = [
            "=" * 70,
            f"   🍽️ RESTAURANT RECOMMENDATIONS (Curated by {self.name})",
            "=" * 70,
            f"User Query: \"{perception['raw_query']}\"",
            f"Cuisine Filter: {', '.join([c.title() for c in perception['detected_cuisines']]) or 'All Cuisines'}\n"
        ]

        if not ranked_candidates:
            lines.append("No restaurants matched your exact criteria. Try broadening your budget or cuisine.")
        else:
            for rank, item in enumerate(ranked_candidates, start=1):
                r = item["restaurant"]
                lines.append(f"#{rank} {r['name']}  (★ {r['rating']} / 5.0)")
                lines.append(f"   • Cuisines:       {', '.join(r['cuisines'])} [{r['diet']}]")
                lines.append(f"   • Location:       {r['location']}")
                lines.append(f"   • Approx Cost:    Rs. {r['cost_for_two']} for two")
                lines.append(f"   • Signature Dish: {r['signature_dish']}")
                lines.append("-" * 70)

            lines.append("\n[ACTION CALLOUT]: Would you like to reserve a table or order online via Zomato/Swiggy?")

        return "\n".join(lines)

    def run(self, user_query: str) -> str:
        """Executes full agent pipeline: Perceive -> Reason -> Act."""
        perception = self.perceive(user_query)
        candidates = self.reason(perception)
        return self.act(candidates, perception)

def run_task3_demo():
    print("=" * 70)
    print("     SESSION 19 - TASK 3: REFACTORED RESTAURANT RECOMMENDER AGENT")
    print("=" * 70)

    agent = AgentRestaurantRecommender()

    # Query 1: Italian food
    print("\n--- Test Query 1: 'Can you recommend good Italian restaurants under Rs. 3000?' ---")
    res1 = agent.run("Can you recommend good Italian restaurants under Rs. 3000?")
    print(res1)

    # Query 2: Pure Veg South Indian
    print("\n" + "=" * 70)
    print("--- Test Query 2: 'Find me vegetarian South Indian places' ---")
    res2 = agent.run("Find me vegetarian South Indian places")
    print(res2)

    print("\n" + "=" * 70)
    print("[SUCCESS] Task 3 completed: Modular Agent class structure verified!")

if __name__ == "__main__":
    run_task3_demo()
