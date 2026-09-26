"""
Session 20 - Task 1: Independent Multi-Agent Flipkart Shopping Assistant
------------------------------------------------------------------------
This script implements two independent agent classes:
1. SearchAgent: Takes a search query and returns matching products from a catalog.
2. RecommendationAgent: Takes a user ID and returns three personalized product recommendations.
Both agents operate independently to simulate a modular e-commerce assistant architecture.
"""

import sys
import re
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# Hardcoded Flipkart Product Catalog
# ============================================================================
FLIPKART_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "PROD-101",
        "title": "Apple iPhone 15 (Black, 128 GB)",
        "brand": "Apple",
        "category": "Smartphones",
        "price_inr": 69999,
        "rating": 4.6,
        "reviews_count": 18450,
        "tags": ["apple", "iphone", "ios", "5g", "oled", "smartphone", "mobile"],
        "in_stock": True,
    },
    {
        "id": "PROD-102",
        "title": "Samsung Galaxy S24 5G (Onyx Black, 256 GB)",
        "brand": "Samsung",
        "category": "Smartphones",
        "price_inr": 74999,
        "rating": 4.5,
        "reviews_count": 9230,
        "tags": ["samsung", "galaxy", "android", "5g", "ai", "smartphone", "mobile"],
        "in_stock": True,
    },
    {
        "id": "PROD-103",
        "title": "OnePlus Nord CE 4 (Dark Chrome, 128 GB)",
        "brand": "OnePlus",
        "category": "Smartphones",
        "price_inr": 24999,
        "rating": 4.3,
        "reviews_count": 31200,
        "tags": ["oneplus", "nord", "android", "5g", "budget", "fast charging", "smartphone"],
        "in_stock": True,
    },
    {
        "id": "PROD-104",
        "title": "ASUS ROG Strix G16 Gaming Laptop (Intel i7 13th Gen, RTX 4060, 16GB RAM)",
        "brand": "ASUS",
        "category": "Laptops",
        "price_inr": 114990,
        "rating": 4.7,
        "reviews_count": 4120,
        "tags": ["asus", "rog", "gaming", "laptop", "rtx 4060", "intel i7", "144hz"],
        "in_stock": True,
    },
    {
        "id": "PROD-105",
        "title": "Apple MacBook Air M2 (Midnight, 8GB RAM, 256GB SSD)",
        "brand": "Apple",
        "category": "Laptops",
        "price_inr": 89990,
        "rating": 4.8,
        "reviews_count": 14200,
        "tags": ["apple", "macbook", "m2", "laptop", "ultrabook", "lightweight"],
        "in_stock": True,
    },
    {
        "id": "PROD-106",
        "title": "Sony WH-1000XM5 Wireless Active Noise Cancelling Headphones",
        "brand": "Sony",
        "category": "Audio",
        "price_inr": 29990,
        "rating": 4.7,
        "reviews_count": 8940,
        "tags": ["sony", "anc", "wireless", "bluetooth", "noise cancelling", "headphones", "audio"],
        "in_stock": True,
    },
    {
        "id": "PROD-107",
        "title": "boAt Airdopes 161 TWS Earbuds with 40H Playtime",
        "brand": "boAt",
        "category": "Audio",
        "price_inr": 1299,
        "rating": 4.1,
        "reviews_count": 145000,
        "tags": ["boat", "airdopes", "tws", "earbuds", "budget", "wireless", "audio"],
        "in_stock": True,
    },
    {
        "id": "PROD-108",
        "title": "Noise ColorFit Pro 5 Smartwatch (1.85\" AMOLED Display)",
        "brand": "Noise",
        "category": "Wearables",
        "price_inr": 3499,
        "rating": 4.2,
        "reviews_count": 42100,
        "tags": ["noise", "smartwatch", "wearables", "fitness", "amoled", "bluetooth calling"],
        "in_stock": True,
    },
    {
        "id": "PROD-109",
        "title": "Apple Watch Series 9 GPS 45mm (Midnight Aluminium)",
        "brand": "Apple",
        "category": "Wearables",
        "price_inr": 44900,
        "rating": 4.8,
        "reviews_count": 6800,
        "tags": ["apple", "watch", "smartwatch", "wearables", "health", "ecg", "fitness"],
        "in_stock": True,
    },
    {
        "id": "PROD-110",
        "title": "Logitech MX Master 3S Wireless Performance Mouse",
        "brand": "Logitech",
        "category": "Accessories",
        "price_inr": 8995,
        "rating": 4.7,
        "reviews_count": 7650,
        "tags": ["logitech", "mouse", "ergonomic", "wireless", "bluetooth", "productivity"],
        "in_stock": True,
    },
    {
        "id": "PROD-111",
        "title": "Samsung 55-inch Crystal 4K UHD Smart TV",
        "brand": "Samsung",
        "category": "Home Entertainment",
        "price_inr": 42990,
        "rating": 4.4,
        "reviews_count": 19400,
        "tags": ["samsung", "tv", "smart tv", "4k", "uhd", "home entertainment"],
        "in_stock": True,
    }
]


# ============================================================================
# User Profiles for Personalized Recommendations
# ============================================================================
USER_PROFILES: Dict[str, Dict[str, Any]] = {
    "USR-101": {
        "name": "Aarav Sharma",
        "persona": "Hardcore PC Gamer & Tech Enthusiast",
        "preferred_categories": ["Laptops", "Audio", "Accessories"],
        "preferred_tags": ["gaming", "rtx 4060", "wireless", "anc", "high performance"],
        "past_purchases": ["PROD-104"],
    },
    "USR-102": {
        "name": "Priya Nair",
        "persona": "Fitness Athlete & Apple Ecosystem User",
        "preferred_categories": ["Wearables", "Audio", "Smartphones"],
        "preferred_tags": ["apple", "fitness", "health", "smartwatch", "anc"],
        "past_purchases": ["PROD-101", "PROD-109"],
    },
    "USR-103": {
        "name": "Rohan Verma",
        "persona": "Value-for-Money Budget Student Shopper",
        "preferred_categories": ["Smartphones", "Audio", "Wearables"],
        "preferred_tags": ["budget", "fast charging", "tws", "amoled"],
        "past_purchases": ["PROD-103", "PROD-107"],
    }
}


# ============================================================================
# 1. SearchAgent: Query-driven Product Discovery
# ============================================================================
class SearchAgent:
    """
    SearchAgent perceives search queries from users, reasons over product titles,
    categories, and keywords in the catalog, and executes the search action.
    """

    def __init__(self, catalog: Optional[List[Dict[str, Any]]] = None):
        self.catalog = catalog or FLIPKART_CATALOG

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Takes a natural language or keyword query, cleans tokens, and scores
        matching products based on keyword overlap with title, brand, category, and tags.
        """
        clean_query = query.strip().lower()
        if not clean_query:
            return []

        # Tokenize query into alphanumeric words
        tokens = set(re.findall(r"\w+", clean_query))
        scored_products = []

        for item in self.catalog:
            score = 0
            title_lower = item["title"].lower()
            category_lower = item["category"].lower()
            brand_lower = item["brand"].lower()
            tags = [t.lower() for t in item.get("tags", [])]

            # Exact phrase match gives highest boost
            if clean_query in title_lower:
                score += 15
            if clean_query in category_lower:
                score += 10

            # Token overlap scoring
            for token in tokens:
                if token in title_lower:
                    score += 5
                if token == brand_lower:
                    score += 8
                if token in category_lower:
                    score += 6
                if token in tags:
                    score += 4

            if score > 0:
                scored_products.append({**item, "_search_score": score})

        # Sort descending by match score, tie-break by rating
        scored_products.sort(key=lambda x: (x["_search_score"], x["rating"]), reverse=True)
        return scored_products[:max_results]

    def format_search_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Helper to render search results nicely in the terminal."""
        lines = [
            f"[SearchAgent] Query: '{query}' | Matches Found: {len(results)}",
            "-" * 65
        ]
        if not results:
            lines.append("   (No matching products found. Try keywords like 'laptop', 'apple', 'earbuds'.)")
            return "\n".join(lines)

        for idx, item in enumerate(results, 1):
            lines.append(
                f"   {idx}. {item['title']} - ₹{item['price_inr']:,} "
                f"(★ {item['rating']}/5 | {item['reviews_count']:,} reviews)"
            )
            lines.append(f"      Category: {item['category']} | Brand: {item['brand']}")
        return "\n".join(lines)


# ============================================================================
# 2. RecommendationAgent: Profile-driven Personalized Picks
# ============================================================================
class RecommendationAgent:
    """
    RecommendationAgent perceives a user's ID, retrieves their historical
    affinities, and reasons over the product catalog to return exactly 3 top picks.
    """

    def __init__(
        self,
        catalog: Optional[List[Dict[str, Any]]] = None,
        user_profiles: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        self.catalog = catalog or FLIPKART_CATALOG
        self.user_profiles = user_profiles or USER_PROFILES

    def get_recommendations(self, user_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Takes a user ID, identifies user preference vectors (preferred categories and tags),
        scores candidates excluding previously purchased items, and returns top `count` items.
        If user is unknown, returns top-rated trending items.
        """
        user_profile = self.user_profiles.get(user_id)
        scored_candidates = []

        if user_profile:
            pref_cats = set(c.lower() for c in user_profile.get("preferred_categories", []))
            pref_tags = set(t.lower() for t in user_profile.get("preferred_tags", []))
            past_purchases = set(user_profile.get("past_purchases", []))

            for item in self.catalog:
                # Do not recommend recently purchased items
                if item["id"] in past_purchases:
                    continue

                affinity_score = 0
                item_cat = item["category"].lower()
                item_tags = set(t.lower() for t in item.get("tags", []))

                if item_cat in pref_cats:
                    affinity_score += 10
                common_tags = pref_tags.intersection(item_tags)
                affinity_score += len(common_tags) * 4
                # Weight by item quality rating
                affinity_score += item["rating"] * 2

                scored_candidates.append({**item, "_affinity_score": affinity_score})

            scored_candidates.sort(key=lambda x: (x["_affinity_score"], x["rating"]), reverse=True)
        else:
            # Fallback for guest or new user: Top rated & highest review volume
            for item in self.catalog:
                generic_score = item["rating"] * 10 + (item["reviews_count"] / 10000.0)
                scored_candidates.append({**item, "_affinity_score": generic_score})
            scored_candidates.sort(key=lambda x: x["_affinity_score"], reverse=True)

        return scored_candidates[:count]

    def format_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> str:
        """Helper to render recommendations nicely in the terminal."""
        user_info = self.user_profiles.get(user_id)
        user_name = user_info["name"] if user_info else "Guest Shopper"
        persona = user_info["persona"] if user_info else "New Visitor (Trending Picks)"

        lines = [
            f"[RecommendationAgent] Personalized Picks for {user_name} ({user_id})",
            f"   Profile Persona: {persona}",
            "-" * 65
        ]
        for idx, item in enumerate(recommendations, 1):
            lines.append(
                f"   {idx}. [{item['category']}] {item['title']}"
            )
            lines.append(
                f"      Price: ₹{item['price_inr']:,} | Rating: ★ {item['rating']}/5 | Brand: {item['brand']}"
            )
        return "\n".join(lines)


# ============================================================================
# Simulation: Flipkart-style Shopping Assistant
# ============================================================================
def simulate_flipkart_shopping_assistant():
    print("=" * 70)
    print("  FLIPKART MULTI-AGENT SHOPPING ASSISTANT (SESSION 20 - TASK 1)")
    print("=" * 70)

    # Initialize both agents independently
    search_agent = SearchAgent()
    recommendation_agent = RecommendationAgent()

    # 1. Simulate Independent SearchAgent Queries
    test_queries = [
        "gaming laptop rtx",
        "wireless noise cancelling earbuds",
        "apple watch",
        "solar powered flying car"  # Expect empty results
    ]

    print("\n--- PHASE 1: INDEPENDENT SEARCH AGENT SIMULATION ---")
    for query in test_queries:
        results = search_agent.search(query, max_results=3)
        print(search_agent.format_search_results(query, results))
        print()

    # 2. Simulate Independent RecommendationAgent for different users
    test_users = ["USR-101", "USR-102", "USR-103", "USR-GUEST-999"]

    print("\n--- PHASE 2: INDEPENDENT RECOMMENDATION AGENT SIMULATION ---")
    for uid in test_users:
        recs = recommendation_agent.get_recommendations(uid, count=3)
        print(recommendation_agent.format_recommendations(uid, recs))
        print()

    print("=" * 70)
    print("[SUCCESS] Task 1: Both SearchAgent and RecommendationAgent simulated independently!")
    print("=" * 70)


if __name__ == "__main__":
    simulate_flipkart_shopping_assistant()
