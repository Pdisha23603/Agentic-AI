"""
Session 19 - Task 1: Spotify-Style Discover Weekly Agent
=======================================================
This script designs an autonomous recommendation agent that suggests trending
music playlists to users based on their recent listening history.

Modular Architecture:
1. Perception Module: Ingests user listening history, skips, and liked genres.
2. Reasoning Module: Computes genre affinities, novelty scores, and matches with trending playlists.
3. Action Module: Generates and formats the personalized 'Discover Weekly' playlist bundle.
"""

import sys
from typing import Dict, List, Any
from dataclasses import dataclass

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# Trending Playlists & Song Catalog
# ==============================================================================
TRENDING_PLAYLISTS_CATALOG = [
    {
        "id": "PL_SYNTH_01",
        "title": "Retro Synth & Neon Nights",
        "primary_genre": "Synthwave",
        "vibe": "Energetic / Late Night Drive",
        "curator": "Spotify Editorial",
        "popularity_score": 94,
        "tracks": [
            {"title": "Blinding Lights", "artist": "The Weeknd", "genre": "Synthwave"},
            {"title": "Midnight City", "artist": "M83", "genre": "Synthwave"},
            {"title": "Nightcall", "artist": "Kavinsky", "genre": "Synthwave"}
        ]
    },
    {
        "id": "PL_INDIE_02",
        "title": "Indie Pop Café",
        "primary_genre": "Indie Pop",
        "vibe": "Chill / Acoustic",
        "curator": "Spotify Indie Hub",
        "popularity_score": 89,
        "tracks": [
            {"title": "As It Was", "artist": "Harry Styles", "genre": "Indie Pop"},
            {"title": "Heat Waves", "artist": "Glass Animals", "genre": "Indie Pop"},
            {"title": "Riptide", "artist": "Vance Joy", "genre": "Indie Pop"}
        ]
    },
    {
        "id": "PL_DANCE_03",
        "title": "Dance Pop Explosion",
        "primary_genre": "Dance-Pop",
        "vibe": "Upbeat / Workout",
        "curator": "Spotify Club Hits",
        "popularity_score": 96,
        "tracks": [
            {"title": "Espresso", "artist": "Sabrina Carpenter", "genre": "Dance-Pop"},
            {"title": "Levitating", "artist": "Dua Lipa", "genre": "Dance-Pop"},
            {"title": "Flowers", "artist": "Miley Cyrus", "genre": "Dance-Pop"}
        ]
    },
    {
        "id": "PL_ROCK_04",
        "title": "Modern Rock Revival",
        "primary_genre": "Rock",
        "vibe": "High Energy / Anthemic",
        "curator": "Rock Nation",
        "popularity_score": 85,
        "tracks": [
            {"title": "Beggin'", "artist": "Måneskin", "genre": "Rock"},
            {"title": "Do I Wanna Know?", "artist": "Arctic Monkeys", "genre": "Rock"}
        ]
    }
]

# ==============================================================================
# The Spotify Discover Weekly Agent Class
# ==============================================================================
class SpotifyDiscoverWeeklyAgent:
    """
    Autonomous recommendation agent structured into:
    - perceive(): Parses listening events and extracts listening patterns
    - reason(): Matches profile against trending playlists with affinity scoring
    - act(): Formats and delivers the customized Discover Weekly package
    """

    def __init__(self, agent_name: str = "DiscoverWeekly-AI"):
        self.agent_name = agent_name

    # 1. PERCEPTION MODULE
    def perceive(self, user_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests user listening stream, track repeat counts, and skip counts.
        Extracts dominant genres and acoustic preferences.
        """
        user_name = user_history.get("user_name", "Listener")
        recent_tracks = user_history.get("recent_tracks", [])
        liked_genres = user_history.get("liked_genres", [])

        # Compute genre frequency weights
        genre_weights = {}
        for genre in liked_genres:
            genre_weights[genre] = genre_weights.get(genre, 0) + 2.0

        for track in recent_tracks:
            g = track.get("genre")
            played_pct = track.get("completed_pct", 100)
            if played_pct > 80:  # Finished song: positive signal
                genre_weights[g] = genre_weights.get(g, 0) + 1.5
            elif played_pct < 30:  # Skipped early: negative signal
                genre_weights[g] = genre_weights.get(g, 0) - 1.0

        # Find top genres
        sorted_genres = sorted(genre_weights.items(), key=lambda x: x[1], reverse=True)
        top_genres = [g[0] for g in sorted_genres if g[1] > 0]

        perception_data = {
            "user_name": user_name,
            "top_genres": top_genres,
            "genre_weights": genre_weights,
            "recently_played_titles": [t["title"] for t in recent_tracks],
            "total_tracks_analyzed": len(recent_tracks)
        }
        return perception_data

    # 2. REASONING MODULE
    def reason(self, perception_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compares user's top genres against the trending playlist catalog.
        Scores candidate playlists based on genre affinity and trending popularity.
        """
        top_genres = perception_data["top_genres"]
        genre_weights = perception_data["genre_weights"]
        played_titles = set(perception_data["recently_played_titles"])

        scored_recommendations = []

        for pl in TRENDING_PLAYLISTS_CATALOG:
            genre = pl["primary_genre"]
            affinity_score = genre_weights.get(genre, 0.0)

            # Calculate bonus for trending popularity
            popularity_bonus = (pl["popularity_score"] / 100.0) * 1.5
            total_score = affinity_score + popularity_bonus

            # Recommend if genre has positive affinity
            if affinity_score > 0:
                # Filter tracks: suggest tracks not yet in recent history
                fresh_tracks = [t for t in pl["tracks"] if t["title"] not in played_titles]

                scored_recommendations.append({
                    "playlist_id": pl["id"],
                    "playlist_title": pl["title"],
                    "genre": genre,
                    "vibe": pl["vibe"],
                    "relevance_score": round(total_score, 2),
                    "fresh_tracks": fresh_tracks if fresh_tracks else pl["tracks"][:2],
                    "rationale": f"Based on your high engagement with {genre} tracks."
                })

        # Sort recommendations by highest score
        scored_recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_recommendations

    # 3. ACTION MODULE
    def act(self, user_name: str, recommendations: List[Dict[str, Any]]) -> str:
        """
        Generates and delivers the personalized Discover Weekly recommendation package.
        """
        output = [
            "=" * 70,
            f"   🎧 SPOTIFY DISCOVER WEEKLY FOR {user_name.upper()}",
            f"   Curated by Agent: {self.agent_name}",
            "=" * 70,
            f"\nHey {user_name}! Based on your recent listening patterns, we curated",
            f"the top trending playlists and tracks tailored to your music taste:\n"
        ]

        for rank, rec in enumerate(recommendations, start=1):
            output.append(f"#{rank} {rec['playlist_title']}  [Score: {rec['relevance_score']}]")
            output.append(f"   • Genre / Vibe:  {rec['genre']} ({rec['vibe']})")
            output.append(f"   • Why Chosen:    {rec['rationale']}")
            output.append("   • Highlight Tracks to Discover:")
            for track in rec["fresh_tracks"]:
                output.append(f"     ▶ {track['title']} - {track['artist']}")
            output.append("-" * 70)

        output.append("\n[ACTION COMPLETE] Playlist bundle pushed to user's Spotify home feed!")
        return "\n".join(output)

    def run(self, user_history: Dict[str, Any]) -> str:
        """Executes full agent loop: Perception -> Reasoning -> Action."""
        perception = self.perceive(user_history)
        recommendations = self.reason(perception)
        return self.act(perception["user_name"], recommendations)

def run_task1_demo():
    agent = SpotifyDiscoverWeeklyAgent()

    # Sample user listening profile
    sample_user_profile = {
        "user_name": "Nishant",
        "liked_genres": ["Synthwave", "Dance-Pop"],
        "recent_tracks": [
            {"title": "Blinding Lights", "artist": "The Weeknd", "genre": "Synthwave", "completed_pct": 100},
            {"title": "Espresso", "artist": "Sabrina Carpenter", "genre": "Dance-Pop", "completed_pct": 95},
            {"title": "Levitating", "artist": "Dua Lipa", "genre": "Dance-Pop", "completed_pct": 100},
            {"title": "Random Metal Song", "artist": "Unknown", "genre": "Metal", "completed_pct": 10}  # Skipped
        ]
    }

    result = agent.run(sample_user_profile)
    print(result)

if __name__ == "__main__":
    run_task1_demo()
