"""
Session 20 - Task 2: MultiAgentManager for Spotify Assistant
-----------------------------------------------------------
This script implements a MultiAgentManager coordinating communication between:
1. ChatAgent: Handles natural language user queries and user interaction.
2. PlaylistAgent: Specializes in generating customized music playlists.

When the user asks for a playlist, the ChatAgent identifies the intent,
routes the request through MultiAgentManager to PlaylistAgent, and formats
the response back to the user.
"""

import sys
import re
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# Music Track Repository for Simulated Playlist Generation
# ============================================================================
MUSIC_CATALOG: Dict[str, List[Dict[str, str]]] = {
    "workout": [
        {"title": "Stronger", "artist": "Kanye West", "duration": "5:11", "bpm": "104", "genre": "Hip-Hop"},
        {"title": "Till I Collapse", "artist": "Eminem ft. Nate Dogg", "duration": "4:57", "bpm": "171", "genre": "Hip-Hop"},
        {"title": "Eye of the Tiger", "artist": "Survivor", "duration": "4:05", "bpm": "109", "genre": "Rock"},
        {"title": "Can't Hold Us", "artist": "Macklemore & Ryan Lewis", "duration": "4:18", "bpm": "146", "genre": "Hip-Hop"},
        {"title": "Titanium", "artist": "David Guetta ft. Sia", "duration": "4:05", "bpm": "126", "genre": "EDM"},
    ],
    "lofi": [
        {"title": "Coffee Breath", "artist": "Kowloon", "duration": "2:34", "bpm": "78", "genre": "Lofi Hip-Hop"},
        {"title": "Raindrops on Glass", "artist": "Nohidea", "duration": "2:45", "bpm": "75", "genre": "Chillhop"},
        {"title": "Midnight Thoughts", "artist": "Idealism", "duration": "3:10", "bpm": "80", "genre": "Lofi"},
        {"title": "Study Session", "artist": "ChilledCow / Lofi Girl", "duration": "2:52", "bpm": "72", "genre": "Lofi"},
        {"title": "Warm Autumn", "artist": "Aiguille", "duration": "2:20", "bpm": "84", "genre": "Chillhop"},
    ],
    "party": [
        {"title": "Levitating", "artist": "Dua Lipa", "duration": "3:23", "bpm": "103", "genre": "Pop / Dance"},
        {"title": "Blinding Lights", "artist": "The Weeknd", "duration": "3:20", "bpm": "171", "genre": "Synthpop"},
        {"title": "One Kiss", "artist": "Calvin Harris & Dua Lipa", "duration": "3:34", "bpm": "124", "genre": "House"},
        {"title": "Despacito", "artist": "Luis Fonsi & Daddy Yankee", "duration": "3:48", "bpm": "89", "genre": "Reggaeton"},
        {"title": "24K Magic", "artist": "Bruno Mars", "duration": "3:46", "bpm": "106", "genre": "Funk / Pop"},
    ],
    "chill": [
        {"title": "Sunflower", "artist": "Post Malone & Swae Lee", "duration": "2:38", "bpm": "90", "genre": "Melodic Rap"},
        {"title": "Slow Dancing in a Burning Room", "artist": "John Mayer", "duration": "4:02", "bpm": "67", "genre": "Blues Rock"},
        {"title": "Sunset Lover", "artist": "Petit Biscuit", "duration": "3:57", "bpm": "91", "genre": "Chillwave"},
        {"title": "Golden Hour", "artist": "JVKE", "duration": "3:29", "bpm": "94", "genre": "Indie Pop"},
        {"title": "Weightless", "artist": "Marconi Union", "duration": "8:00", "bpm": "60", "genre": "Ambient"},
    ],
    "bollywood": [
        {"title": "Kesariya", "artist": "Arijit Singh, Pritam", "duration": "4:28", "bpm": "95", "genre": "Bollywood Romantic"},
        {"title": "Apna Bana Le", "artist": "Arijit Singh, Sachin-Jigar", "duration": "4:21", "bpm": "88", "genre": "Bollywood Melodic"},
        {"title": "Chaleya", "artist": "Arijit Singh, Shilpa Rao, Anirudh", "duration": "3:20", "bpm": "102", "genre": "Bollywood Pop"},
        {"title": "Ilahi", "artist": "Arijit Singh, Pritam", "duration": "3:49", "bpm": "128", "genre": "Bollywood Travel"},
        {"title": "Badtameez Dil", "artist": "Benny Dayal, Pritam", "duration": "4:12", "bpm": "140", "genre": "Bollywood Party"},
    ]
}


# ============================================================================
# PlaylistAgent: Music Curator & Generator
# ============================================================================
class PlaylistAgent:
    """
    PlaylistAgent is responsible for domain-specific music intelligence.
    It perceives playlist requirements (mood, genre, activity), reasons over
    the track repository, and builds structured playlists.
    """

    def __init__(self):
        self.catalog = MUSIC_CATALOG

    def create_playlist(self, mood_or_genre: str, track_count: int = 4) -> Dict[str, Any]:
        """
        Creates a curated playlist matching the requested mood or genre.
        """
        key = mood_or_genre.lower().strip()
        matched_category = "chill"  # Default fallback

        for cat in self.catalog.keys():
            if cat in key:
                matched_category = cat
                break

        selected_tracks = self.catalog.get(matched_category, self.catalog["chill"])[:track_count]

        playlist_titles = {
            "workout": "Beast Mode High Energy",
            "lofi": "Late Night Deep Focus Lofi",
            "party": "Club Hits & Floor Fillers",
            "chill": "Relax & Unwind Melodic Vibez",
            "bollywood": "Top Bollywood Melodies & Beats"
        }

        playlist_name = playlist_titles.get(matched_category, f"Custom {matched_category.capitalize()} Mix")

        return {
            "status": "success",
            "playlist_name": playlist_name,
            "category": matched_category,
            "total_tracks": len(selected_tracks),
            "tracks": selected_tracks,
            "curator": "PlaylistAgent (v2.1)"
        }


# ============================================================================
# ChatAgent: Natural Language & User Interaction Agent
# ============================================================================
class ChatAgent:
    """
    ChatAgent acts as the front-facing conversational representative.
    It interprets user intent and delegates domain operations to the manager.
    """

    def __init__(self, manager: Optional["MultiAgentManager"] = None):
        self.manager = manager

    def set_manager(self, manager: "MultiAgentManager"):
        self.manager = manager

    def process_message(self, user_query: str) -> str:
        """
        Perceives user query, reasons on intent (General Chat vs Playlist Request),
        and invokes action either locally or by communicating with PlaylistAgent.
        """
        clean_query = user_query.lower()

        # Check for Playlist Creation Intent
        playlist_keywords = ["playlist", "songs", "tracks", "music", "workout", "lofi", "party", "chill", "bollywood"]
        is_playlist_request = any(kw in clean_query for kw in playlist_keywords)

        if is_playlist_request:
            # Determine mood / theme from query
            detected_theme = "chill"
            for theme in ["workout", "lofi", "party", "bollywood", "chill"]:
                if theme in clean_query:
                    detected_theme = theme
                    break

            if not self.manager:
                return "[ChatAgent] Error: No MultiAgentManager attached to coordinate with PlaylistAgent."

            # Coordinate communication: delegate playlist creation to PlaylistAgent via manager
            print(f"  [ChatAgent] -> Delegating playlist request ('{detected_theme}') to PlaylistAgent via MultiAgentManager...")
            playlist_result = self.manager.delegate_task(
                target_agent="PlaylistAgent",
                action="create_playlist",
                payload={"mood_or_genre": detected_theme, "track_count": 4}
            )

            # Format the coordinated response
            return self._format_playlist_response(user_query, playlist_result)

        # Conversational / FAQ intent handling
        if any(g in clean_query for g in ["hi", "hello", "hey", "who are you"]):
            return (
                "[ChatAgent] Hello! I'm your Spotify AI Assistant. I can chat with you and create custom "
                "playlists for workout, lofi study, party, bollywood, or chill vibes. What are you in the mood for?"
            )
        elif "help" in clean_query:
            return (
                "[ChatAgent] You can ask me things like:\n"
                "  - 'Create a high-energy workout playlist for the gym'\n"
                "  - 'Can you make me a calming lofi playlist for coding?'\n"
                "  - 'Give me a party mix for tonight!'"
            )
        else:
            return (
                f"[ChatAgent] I heard: '{user_query}'. I can assemble a custom playlist for you! "
                "Just let me know your preferred vibe (e.g., workout, lofi, party, bollywood, or chill)."
            )

    def _format_playlist_response(self, user_query: str, playlist_data: Dict[str, Any]) -> str:
        """Synthesizes human-friendly response presenting the playlist."""
        if not playlist_data or playlist_data.get("status") != "success":
            return "[ChatAgent] Sorry, I encountered an issue retrieving the playlist from PlaylistAgent."

        lines = [
            f"[ChatAgent] Here is your custom Spotify playlist tailored for you!",
            f"   🎵 Playlist: \"{playlist_data['playlist_name']}\" ({playlist_data['total_tracks']} Tracks)",
            f"   🏷 Category: {playlist_data['category'].capitalize()} | Curated by: {playlist_data['curator']}",
            "   " + "-" * 55
        ]
        for idx, track in enumerate(playlist_data["tracks"], 1):
            lines.append(
                f"   {idx}. {track['title']} - {track['artist']} [{track['duration']}] (BPM: {track['bpm']})"
            )
        lines.append("   " + "-" * 55)
        lines.append("   Enjoy your listening session! Let me know if you want to swap any tracks.")
        return "\n".join(lines)


# ============================================================================
# MultiAgentManager: Multi-Agent Coordinator
# ============================================================================
class MultiAgentManager:
    """
    MultiAgentManager coordinates message passing and task delegation between
    registered agents (ChatAgent, PlaylistAgent, etc.).
    """

    def __init__(self):
        self.registry: Dict[str, Any] = {}

    def register_agent(self, agent_name: str, agent_instance: Any):
        """Registers an agent into the manager's ecosystem."""
        self.registry[agent_name] = agent_instance
        # Give the agent a back-reference to this manager if supported
        if hasattr(agent_instance, "set_manager"):
            agent_instance.set_manager(self)
        print(f"[*] MultiAgentManager: Registered agent '{agent_name}'.")

    def delegate_task(self, target_agent: str, action: str, payload: Dict[str, Any]) -> Any:
        """
        Dispatches a task from one agent to another and returns the resulting output.
        """
        agent = self.registry.get(target_agent)
        if not agent:
            raise ValueError(f"Agent '{target_agent}' not found in MultiAgentManager registry.")

        if hasattr(agent, action):
            func = getattr(agent, action)
            return func(**payload)
        else:
            raise AttributeError(f"Agent '{target_agent}' has no action method '{action}'.")

    def handle_user_query(self, user_message: str) -> str:
        """
        Main entry point for incoming user queries.
        Routes the prompt to ChatAgent to initiate the multi-agent workflow.
        """
        chat_agent: Optional[ChatAgent] = self.registry.get("ChatAgent")
        if not chat_agent:
            return "[MultiAgentManager] Error: No ChatAgent registered to handle user input."
        return chat_agent.process_message(user_message)


# ============================================================================
# Simulation Demonstration
# ============================================================================
def simulate_spotify_multi_agent_system():
    print("=" * 70)
    print("  SPOTIFY MULTI-AGENT ASSISTANT (SESSION 20 - TASK 2)")
    print("=" * 70)

    # 1. Initialize Agents & Manager
    manager = MultiAgentManager()
    chat_agent = ChatAgent()
    playlist_agent = PlaylistAgent()

    # 2. Register Agents
    manager.register_agent("ChatAgent", chat_agent)
    manager.register_agent("PlaylistAgent", playlist_agent)
    print()

    # 3. Simulate Conversations
    conversation_prompts = [
        "Hello! Who are you?",
        "I'm hitting the gym for leg day. Create an intense workout playlist for me!",
        "Can you build me a calming lofi beats playlist to help me code late at night?",
        "Throw together an awesome bollywood playlist for a party!",
        "What is the meaning of life?"
    ]

    for idx, prompt in enumerate(conversation_prompts, 1):
        print(f"\n--- Interaction #{idx} ---")
        print(f"User: \"{prompt}\"")
        response = manager.handle_user_query(prompt)
        print(response)

    print("\n" + "=" * 70)
    print("[SUCCESS] Task 2: MultiAgentManager successfully coordinated ChatAgent and PlaylistAgent!")
    print("=" * 70)


if __name__ == "__main__":
    simulate_spotify_multi_agent_system()
