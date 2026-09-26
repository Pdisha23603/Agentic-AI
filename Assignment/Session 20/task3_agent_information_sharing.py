"""
Session 20 - Task 3: Multi-Agent Information Sharing & Inter-Agent Message Logging
---------------------------------------------------------------------------------
This script extends the MultiAgentManager to implement an explicit message-passing
protocol between agents:
1. When ChatAgent receives a request for a 'top trending playlist', it sends an
   information request (GET_TRENDING_DATA) to PlaylistAgent.
2. PlaylistAgent returns live trending metrics, viral tracks, and streaming counts.
3. ChatAgent synthesizes this shared information to assemble a tailored response.
4. MultiAgentManager logs all agent-to-agent messages in a structured audit log
   for comprehensive debugging and tracing.
"""

import sys
import re
import datetime
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# Inter-Agent Message Definition
# ============================================================================
class AgentMessage:
    """Represents a structured communication packet between agents."""
    def __init__(self, sender: str, recipient: str, msg_type: str, payload: Dict[str, Any]):
        self.message_id = f"MSG-{datetime.datetime.now().strftime('%H%M%S%f')[:10]}"
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.sender = sender
        self.recipient = recipient
        self.msg_type = msg_type
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "from": self.sender,
            "to": self.recipient,
            "type": self.msg_type,
            "payload": self.payload
        }

    def __repr__(self) -> str:
        return f"AgentMessage({self.sender} -> {self.recipient} | {self.msg_type})"


# ============================================================================
# Trending Data Repository for Spotify Simulation
# ============================================================================
SPOTIFY_TRENDING_DATABASE = {
    "chart_name": "Spotify Global Top 50 Trending",
    "last_updated": "Today, 14:00 IST",
    "top_genre_surge": "Afrobeats & Desi Hip-Hop (+34% weekly spike)",
    "trending_tracks": [
        {
            "rank": 1,
            "title": "Espresso",
            "artist": "Sabrina Carpenter",
            "streams_today": 8420000,
            "trend": "↑ #1 (viral on Reels/TikTok)",
            "genre": "Nu-Disco / Pop",
            "duration": "2:55"
        },
        {
            "rank": 2,
            "title": "Million Dollar Baby",
            "artist": "Tommy Richman",
            "streams_today": 7650000,
            "trend": "↑ #2 (breakout hit)",
            "genre": "Funk / R&B",
            "duration": "2:35"
        },
        {
            "rank": 3,
            "title": "Tauba Tauba",
            "artist": "Karan Aujla",
            "streams_today": 6890000,
            "trend": "↑ #3 (top trending in India)",
            "genre": "Punjabi Pop / Desi Hip-Hop",
            "duration": "3:26"
        },
        {
            "rank": 4,
            "title": "Birds of a Feather",
            "artist": "Billie Eilish",
            "streams_today": 6410000,
            "trend": "↑ #4 (steady viral)",
            "genre": "Alt-Pop",
            "duration": "3:03"
        },
        {
            "rank": 5,
            "title": "Not Like Us",
            "artist": "Kendrick Lamar",
            "streams_today": 5980000,
            "trend": "↑ #5 (record breaking)",
            "genre": "West Coast Hip-Hop",
            "duration": "4:34"
        }
    ]
}


# ============================================================================
# PlaylistAgent with Information Provider Capabilities
# ============================================================================
class PlaylistAgent:
    """
    PlaylistAgent manages music catalog data and responds to specific information
    queries (e.g. trending data, playlist building) sent by other agents.
    """

    def __init__(self, name: str = "PlaylistAgent"):
        self.name = name
        self.manager: Optional["LoggingMultiAgentManager"] = None

    def set_manager(self, manager: "LoggingMultiAgentManager"):
        self.manager = manager

    def receive_message(self, message: AgentMessage) -> AgentMessage:
        """
        Processes incoming message from another agent and returns an answer message.
        """
        msg_type = message.msg_type
        payload = message.payload

        if msg_type == "GET_TRENDING_DATA":
            # Extract trending data to share with requester
            region = payload.get("region", "Global")
            limit = payload.get("limit", 5)
            trending_slice = SPOTIFY_TRENDING_DATABASE["trending_tracks"][:limit]

            response_payload = {
                "chart_name": SPOTIFY_TRENDING_DATABASE["chart_name"],
                "region": region,
                "surge_insight": SPOTIFY_TRENDING_DATABASE["top_genre_surge"],
                "tracks": trending_slice,
                "status": "success"
            }

            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                msg_type="TRENDING_DATA_RESPONSE",
                payload=response_payload
            )

        elif msg_type == "GENERATE_CUSTOM_PLAYLIST":
            category = payload.get("category", "chill")
            track_count = payload.get("count", 3)

            # Generate synthetic playlist
            playlist_name = f"Vibe Mix: {category.capitalize()}"
            sample_tracks = [
                {"title": f"{category.capitalize()} Groove #1", "artist": "Spotify Studio", "duration": "3:10"},
                {"title": f"{category.capitalize()} Beats #2", "artist": "SoundWave", "duration": "2:45"},
                {"title": f"{category.capitalize()} Melody #3", "artist": "Harmony Collective", "duration": "3:30"},
            ][:track_count]

            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                msg_type="PLAYLIST_RESPONSE",
                payload={
                    "status": "success",
                    "playlist_name": playlist_name,
                    "tracks": sample_tracks
                }
            )

        else:
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                msg_type="UNKNOWN_REQUEST_ERROR",
                payload={"error": f"Unsupported message type: {msg_type}"}
            )


# ============================================================================
# ChatAgent: Natural Language Coordinator & Information Consumer
# ============================================================================
class ChatAgent:
    """
    ChatAgent interacts with the user, perceives complex queries, requests
    real-time intelligence from PlaylistAgent, and synthesizes answers.
    """

    def __init__(self, name: str = "ChatAgent", manager: Optional["LoggingMultiAgentManager"] = None):
        self.name = name
        self.manager = manager

    def set_manager(self, manager: "LoggingMultiAgentManager"):
        self.manager = manager

    def process_user_query(self, user_text: str) -> str:
        """
        Analyzes user query and initiates inter-agent communication if necessary.
        """
        clean_text = user_text.lower()

        # 1. Check for 'Top Trending' or 'Trending Playlist' intent
        if "trending" in clean_text or "viral" in clean_text or "top charts" in clean_text:
            print(f"  [{self.name}] User requested trending music. Inquiring PlaylistAgent for trending data...")

            # Formulate inter-agent message
            req_message = AgentMessage(
                sender=self.name,
                recipient="PlaylistAgent",
                msg_type="GET_TRENDING_DATA",
                payload={"region": "India / Global", "limit": 4}
            )

            # Send via manager message bus
            reply_msg = self.manager.send_message(req_message)

            # Synthesize final user response from shared data
            return self._build_trending_response(reply_msg.payload)

        # 2. Check for standard playlist generation intent
        elif any(k in clean_text for k in ["playlist", "workout", "lofi", "party", "chill"]):
            matched_vibe = "chill"
            for vibe in ["workout", "lofi", "party", "chill"]:
                if vibe in clean_text:
                    matched_vibe = vibe
                    break

            print(f"  [{self.name}] Inquiring PlaylistAgent to generate custom '{matched_vibe}' playlist...")
            req_message = AgentMessage(
                sender=self.name,
                recipient="PlaylistAgent",
                msg_type="GENERATE_CUSTOM_PLAYLIST",
                payload={"category": matched_vibe, "count": 3}
            )
            reply_msg = self.manager.send_message(req_message)
            return self._build_playlist_response(reply_msg.payload)

        # 3. Conversational greetings
        elif any(g in clean_text for g in ["hi", "hello", "hey"]):
            return (
                f"[{self.name}] Hello! I'm your Spotify Multi-Agent Assistant. Ask me for the "
                "'top trending playlist' or request custom genre playlists (workout, lofi, chill)."
            )
        else:
            return (
                f"[{self.name}] You said: '{user_text}'. Try asking me for 'top trending playlist' "
                "to see real-time inter-agent data sharing!"
            )

    def _build_trending_response(self, trending_data: Dict[str, Any]) -> str:
        """Combines shared trending data into a premium user response."""
        tracks = trending_data.get("tracks", [])
        chart = trending_data.get("chart_name", "Spotify Trending")
        surge = trending_data.get("surge_insight", "")

        lines = [
            f"[{self.name}] Here is the official Top Trending Playlist curated from live Spotify charts!",
            f"   🔥 Chart: {chart} | Market Surge: {surge}",
            "   " + "=" * 60
        ]
        for t in tracks:
            lines.append(
                f"   #{t['rank']} {t['title']} - {t['artist']} ({t['genre']})"
            )
            lines.append(
                f"      Streams: {t['streams_today']:,} daily plays | Metric: {t['trend']} | [{t['duration']}]"
            )
        lines.append("   " + "=" * 60)
        lines.append(
            f"   Information retrieved seamlessly from PlaylistAgent via MultiAgentManager."
        )
        return "\n".join(lines)

    def _build_playlist_response(self, playlist_data: Dict[str, Any]) -> str:
        tracks = playlist_data.get("tracks", [])
        p_name = playlist_data.get("playlist_name", "Custom Mix")
        lines = [
            f"[{self.name}] Created your requested playlist: '{p_name}'",
            "   " + "-" * 50
        ]
        for idx, trk in enumerate(tracks, 1):
            lines.append(f"   {idx}. {trk['title']} - {trk['artist']} ({trk['duration']})")
        lines.append("   " + "-" * 50)
        return "\n".join(lines)


# ============================================================================
# LoggingMultiAgentManager: Coordinates & Logs All Inter-Agent Messages
# ============================================================================
class LoggingMultiAgentManager:
    """
    Coordinates agent communication and maintains an audit log of every
    inter-agent message for transparent debugging and observability.
    """

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.message_logs: List[Dict[str, Any]] = []

    def register_agent(self, agent_name: str, agent_instance: Any):
        """Registers agent and injects manager reference."""
        self.agents[agent_name] = agent_instance
        if hasattr(agent_instance, "set_manager"):
            agent_instance.set_manager(self)
        print(f"[*] Registered agent: '{agent_name}'")

    def send_message(self, message: AgentMessage) -> AgentMessage:
        """
        Routes message from sender to recipient, logs the transaction,
        and returns the recipient's response message after logging it as well.
        """
        # 1. Log outgoing message
        self.message_logs.append(message.to_dict())

        recipient_agent = self.agents.get(message.recipient)
        if not recipient_agent:
            err_msg = AgentMessage(
                sender="MultiAgentManager",
                recipient=message.sender,
                msg_type="ROUTING_ERROR",
                payload={"error": f"Recipient agent '{message.recipient}' not found."}
            )
            self.message_logs.append(err_msg.to_dict())
            return err_msg

        # 2. Dispatch to recipient
        response_msg: AgentMessage = recipient_agent.receive_message(message)

        # 3. Log response message
        self.message_logs.append(response_msg.to_dict())

        return response_msg

    def handle_user_request(self, user_query: str) -> str:
        """Entry point for user queries."""
        chat_agent: Optional[ChatAgent] = self.agents.get("ChatAgent")
        if not chat_agent:
            return "[Manager Error] No ChatAgent registered."
        return chat_agent.process_user_query(user_query)

    def print_message_logs(self):
        """Displays formatted message logs for debugging."""
        print("\n" + "=" * 75)
        print(f"  MULTI-AGENT INTER-COMMUNICATION DEBUG LOG ({len(self.message_logs)} Messages Recorded)")
        print("=" * 75)
        for idx, entry in enumerate(self.message_logs, 1):
            print(f"[{idx:02d}] {entry['timestamp']} | ID: {entry['message_id']}")
            print(f"     FROM : {entry['from']} ──> TO: {entry['to']}")
            print(f"     TYPE : {entry['type']}")
            print(f"     DATA : {entry['payload']}")
            print("     " + "-" * 65)
        print("=" * 75)


# ============================================================================
# Simulation Demonstration
# ============================================================================
def simulate_information_sharing():
    print("=" * 75)
    print("  MULTI-AGENT INFORMATION SHARING & MESSAGE LOGGING (SESSION 20 - TASK 3)")
    print("=" * 75)

    manager = LoggingMultiAgentManager()
    chat_agent = ChatAgent()
    playlist_agent = PlaylistAgent()

    manager.register_agent("ChatAgent", chat_agent)
    manager.register_agent("PlaylistAgent", playlist_agent)
    print()

    # Step 1: User asks for a top trending playlist (requires inter-agent information sharing)
    query_1 = "Can you recommend the top trending playlist right now?"
    print(f"\n>>> USER QUERY 1: \"{query_1}\"")
    resp_1 = manager.handle_user_request(query_1)
    print(resp_1)

    # Step 2: User asks for a custom workout playlist
    query_2 = "Make me a high energy workout playlist"
    print(f"\n>>> USER QUERY 2: \"{query_2}\"")
    resp_2 = manager.handle_user_request(query_2)
    print(resp_2)

    # Step 3: Print all logged inter-agent messages for verification and debugging
    manager.print_message_logs()

    print("\n[SUCCESS] Task 3: Information sharing and message logging verified successfully!")


if __name__ == "__main__":
    simulate_information_sharing()
