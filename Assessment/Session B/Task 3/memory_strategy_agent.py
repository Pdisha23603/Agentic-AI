"""
Memory-Aware Strategy Selector
--------------------------------
A simple agent for a food-delivery domain that:
  1. Maintains per-user memory across interactions (interaction_count,
     preferred_cuisine, last_complaint).
  2. Chooses one of three response strategies based on query type and
     memory state:
       - fine_tuned_response   -> complaint-type query AFTER 3+ prior interactions
       - rag_lookup_response   -> menu / item / price queries
       - prompt_template_response -> everything else
  3. Updates memory after every interaction.

Run with:  python3 memory_strategy_agent.py
No third-party packages required (pure standard library).
"""

import re

# ---------------------------------------------------------------------
# Global memory store: { user_id: {interaction_count, preferred_cuisine,
#                                    last_complaint} }
# ---------------------------------------------------------------------
memory = {}

COMPLAINT_KEYWORDS = [
    "complaint", "complain", "bad", "wrong", "late", "cold",
    "refund", "issue", "problem", "missing", "terrible", "worst",
    "never arrived", "rude"
]

MENU_KEYWORDS = [
    "menu", "price", "item", "dish", "available", "recommend",
    "recommendation", "options", "cost", "ingredients"
]

CUISINE_KEYWORDS = [
    "italian", "chinese", "indian", "mexican", "thai", "japanese",
    "pizza", "sushi", "burger", "biryani", "pasta"
]


def _init_user(user_id):
    """Create a fresh memory record for a new user."""
    if user_id not in memory:
        memory[user_id] = {
            "interaction_count": 0,
            "preferred_cuisine": None,
            "last_complaint": None,
        }


def _classify_query(query):
    q = query.lower()
    is_complaint = any(kw in q for kw in COMPLAINT_KEYWORDS)
    is_menu = any(kw in q for kw in MENU_KEYWORDS)
    return is_complaint, is_menu


def _detect_cuisine(query):
    q = query.lower()
    for cuisine in CUISINE_KEYWORDS:
        if cuisine in q:
            return cuisine
    return None


# ---------------------------------------------------------------------
# Strategy functions (each returns a simulated, contextual response)
# ---------------------------------------------------------------------
def prompt_template_response(query):
    return (
        f"[Prompt-Template] Thanks for reaching out! Regarding \"{query}\" - "
        f"our standard delivery hours are 9 AM to 11 PM, and you can track "
        f"your order in real time from the app. Let us know if you need anything else!"
    )


def rag_lookup_response(query):
    return (
        f"[RAG-Lookup] Searching our live menu database for \"{query}\"... "
        f"Found matches: Margherita Pizza ($9.99), Chicken Biryani ($11.50), "
        f"Veggie Sushi Roll ($8.75). Prices and availability reflect the "
        f"nearest restaurant partner to your location."
    )


def fine_tuned_response(query):
    return (
        f"[Fine-Tuned-Model] I'm really sorry about the trouble with \"{query}\". "
        f"Based on your order history, this looks similar to a past issue, so "
        f"I've escalated it to priority support and issued a goodwill credit "
        f"to your account. You should see it reflected within 24 hours."
    )


# ---------------------------------------------------------------------
# Strategy decision logic
# ---------------------------------------------------------------------
def decide_strategy(user_id, query):
    _init_user(user_id)
    user_mem = memory[user_id]

    is_complaint, is_menu = _classify_query(query)

    # Decision rules (evaluated using memory state BEFORE this interaction
    # is counted, i.e. "3+ prior interactions")
    if is_complaint and user_mem["interaction_count"] >= 3:
        strategy = "fine_tuned"
        response = fine_tuned_response(query)
    elif is_menu:
        strategy = "rag_lookup"
        response = rag_lookup_response(query)
    else:
        strategy = "prompt_template"
        response = prompt_template_response(query)

    # ---- Update memory after the interaction ----
    user_mem["interaction_count"] += 1

    if is_complaint:
        user_mem["last_complaint"] = query

    cuisine = _detect_cuisine(query)
    if cuisine:
        user_mem["preferred_cuisine"] = cuisine

    return strategy, response


# ---------------------------------------------------------------------
# Demo: simulate a sequence of interactions for the same user
# ---------------------------------------------------------------------
def run_demo():
    user_id = "user_101"

    queries = [
        "Hi, what are your delivery hours?",                     # prompt_template
        "Can you show me the menu for Italian food?",             # rag_lookup + cuisine detected
        "What items and prices do you have for biryani?",         # rag_lookup + cuisine detected
        "My order arrived cold and late, this is terrible!",      # complaint, but <3 prior -> prompt_template
        "This is the second time my food arrived cold, I want a refund!",  # complaint, 3+ prior -> fine_tuned
    ]

    print("=" * 70)
    print(f"Simulating interactions for user_id = '{user_id}'")
    print("=" * 70)

    for i, query in enumerate(queries, start=1):
        strategy, response = decide_strategy(user_id, query)

        print(f"\nInteraction #{i}")
        print(f"  Query      : {query}")
        print(f"  Strategy   : {strategy}")
        print(f"  Response   : {response}")
        print(f"  Memory now : {memory[user_id]}")

    print("\n" + "=" * 70)
    print("Final memory state for all users:")
    print(memory)


if __name__ == "__main__":
    run_demo()
