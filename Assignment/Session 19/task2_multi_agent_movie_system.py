"""
Session 19 - Task 2: Multi-Agent Movie Recommendation System
============================================================
This script implements a multi-agent system with function-call communication:
- Agent 1 (MovieDiscoveryAgent): Fetches and provides latest movie releases.
- Agent 2 (MovieRecommendationAgent): Communicates with Agent 1 via function call,
  filters movies by user's preferred genres, and generates personalized recommendations.
"""

import sys
from typing import List, Dict, Any

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# Simulated Latest Movie Releases Catalog
# ==============================================================================
LATEST_RELEASES_DATABASE = [
    {
        "id": "MOV_01",
        "title": "Dune: Part Two",
        "genres": ["Sci-Fi", "Adventure", "Action"],
        "imdb_rating": 8.6,
        "runtime": "166 min",
        "director": "Denis Villeneuve",
        "synopsis": "Paul Atreides unites with the Fremen people while seeking revenge against the conspirators."
    },
    {
        "id": "MOV_02",
        "title": "Kalki 2898 AD",
        "genres": ["Sci-Fi", "Action", "Mythology"],
        "imdb_rating": 8.1,
        "runtime": "180 min",
        "director": "Nag Ashwin",
        "synopsis": "A modern avatar of Vishnu descends to protect the world from dark totalitarian forces in 2898 AD."
    },
    {
        "id": "MOV_03",
        "title": "Inside Out 2",
        "genres": ["Animation", "Comedy", "Family"],
        "imdb_rating": 7.7,
        "runtime": "96 min",
        "director": "Kelsey Mann",
        "synopsis": "Joy and Sadness navigate Riley's mind as Anxiety and brand-new teenage emotions arrive."
    },
    {
        "id": "MOV_04",
        "title": "Deadpool & Wolverine",
        "genres": ["Action", "Comedy", "Sci-Fi"],
        "imdb_rating": 7.8,
        "runtime": "128 min",
        "director": "Shawn Levy",
        "synopsis": "Wade Wilson teams up with a reluctant Wolverine on a mission that changes the multiverse."
    },
    {
        "id": "MOV_05",
        "title": "A Quiet Place: Day One",
        "genres": ["Horror", "Drama", "Sci-Fi"],
        "imdb_rating": 6.8,
        "runtime": "99 min",
        "director": "Michael Sarnoski",
        "synopsis": "Experience the terrifying day the world went silent when alien predators arrived in New York City."
    },
    {
        "id": "MOV_06",
        "title": "Stree 2",
        "genres": ["Comedy", "Horror"],
        "imdb_rating": 7.6,
        "runtime": "147 min",
        "director": "Amar Kaushik",
        "synopsis": "The town of Chanderi is haunted once more, this time by a headless entity named Sarkata."
    }
]

# ==============================================================================
# AGENT 1: Movie Discovery Agent
# ==============================================================================
class MovieDiscoveryAgent:
    """
    Agent responsible for monitoring theater and streaming releases,
    serving candidate movie lists to other consumer agents.
    """

    def __init__(self, name: str = "DiscoveryAgent"):
        self.name = name
        self.catalog = LATEST_RELEASES_DATABASE

    def fetch_latest_releases(self, min_rating: float = 0.0) -> List[Dict[str, Any]]:
        """
        Callable function endpoint exposed to other agents.
        Returns filtered list of new releases.
        """
        print(f"[{self.name}] Received function call: fetch_latest_releases(min_rating={min_rating})")
        qualified_movies = [
            m for m in self.catalog
            if m["imdb_rating"] >= min_rating
        ]
        print(f"[{self.name}] Discovered {len(qualified_movies)} releases meeting criteria.")
        return qualified_movies

# ==============================================================================
# AGENT 2: Movie Recommendation Agent
# ==============================================================================
class MovieRecommendationAgent:
    """
    Agent responsible for reasoning over user taste profiles and
    communicating with MovieDiscoveryAgent to curate watchlist suggestions.
    """

    def __init__(self, discovery_agent: MovieDiscoveryAgent, name: str = "RecommendationAgent"):
        self.name = name
        self.discovery_agent = discovery_agent  # Direct reference for agent-to-agent communication

    def suggest_movies(self, user_name: str, preferred_genres: List[str]) -> str:
        """
        Coordinates the recommendation workflow:
        1. Calls discovery_agent.fetch_latest_releases()
        2. Filters and scores candidates matching user preferences
        3. Formulates recommendation response
        """
        print(f"\n[{self.name}] Initiating recommendation request for user '{user_name}'")
        print(f"[{self.name}] User Preferred Genres: {preferred_genres}")

        # FUNCTION CALL: Agent 2 calls Agent 1
        print(f"[{self.name}] Calling DiscoveryAgent via function invocation...")
        latest_movies = self.discovery_agent.fetch_latest_releases(min_rating=7.0)

        # Reasoning: Match and score movies
        user_genres_set = set(g.lower() for g in preferred_genres)
        matched_recommendations = []

        for movie in latest_movies:
            movie_genres = set(g.lower() for g in movie["genres"])
            common_genres = user_genres_set.intersection(movie_genres)

            if common_genres:
                match_score = len(common_genres) * 2.0 + movie["imdb_rating"]
                matched_recommendations.append({
                    "movie": movie,
                    "matched_genres": list(common_genres),
                    "score": round(match_score, 1)
                })

        # Sort by match score descending
        matched_recommendations.sort(key=lambda x: x["score"], reverse=True)

        # Action: Synthesize response
        return self._format_response(user_name, preferred_genres, matched_recommendations)

    def _format_response(self, user_name: str, preferred_genres: List[str], recommendations: List[Dict]) -> str:
        lines = [
            "=" * 70,
            f"   🎬 PERSONALIZED MOVIE RECOMMENDATIONS FOR {user_name.upper()}",
            f"   Curated by: {self.name}  (Powered by {self.discovery_agent.name})",
            "=" * 70,
            f"\nUser Interests: {', '.join(preferred_genres)}\n"
        ]

        if not recommendations:
            lines.append("No current new releases matched your preferred genres.")
        else:
            for rank, item in enumerate(recommendations, start=1):
                m = item["movie"]
                matched = ", ".join(item["matched_genres"]).title()
                lines.append(f"#{rank} {m['title']} (★ {m['imdb_rating']} / 10)")
                lines.append(f"   • Genres:       {', '.join(m['genres'])} [Matched: {matched}]")
                lines.append(f"   • Director:     {m['director']} | Runtime: {m['runtime']}")
                lines.append(f"   • Synopsis:     {m['synopsis']}")
                lines.append("-" * 70)

        lines.append(f"\n[AGENT-TO-AGENT TRACE]: MovieRecommendationAgent ➔ MovieDiscoveryAgent call successful.")
        return "\n".join(lines)

def run_task2_demo():
    print("=" * 70)
    print("    SESSION 19 - TASK 2: MULTI-AGENT MOVIE RECOMMENDATION SYSTEM")
    print("=" * 70)

    # 1. Instantiate Agents
    discovery_agent = MovieDiscoveryAgent(name="ReleaseDiscoveryAgent-1")
    recommender_agent = MovieRecommendationAgent(discovery_agent=discovery_agent, name="TasteCuratorAgent-2")

    # 2. Test Case 1: Sci-Fi & Action enthusiast
    result_1 = recommender_agent.suggest_movies(
        user_name="Nishant",
        preferred_genres=["Sci-Fi", "Action"]
    )
    print(result_1)

    # 3. Test Case 2: Comedy enthusiast
    print("\n" + "=" * 70 + "\n")
    result_2 = recommender_agent.suggest_movies(
        user_name="Priya",
        preferred_genres=["Comedy", "Animation"]
    )
    print(result_2)

if __name__ == "__main__":
    run_task2_demo()
