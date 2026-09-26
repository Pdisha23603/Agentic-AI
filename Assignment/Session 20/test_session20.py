"""
Session 20 - Automated Comprehensive Test Suite
----------------------------------------------
Validates Task 1, Task 2, Task 3, and Task 4 implementations:
- Task 1: SearchAgent & RecommendationAgent Flipkart simulation.
- Task 2: MultiAgentManager coordinating ChatAgent & PlaylistAgent.
- Task 3: Multi-agent information sharing, message bus & audit logging.
- Task 4: IPL multi-agent score fetcher and analytical summary synthesizer.
"""

import sys
import os
import unittest

# Ensure script directory is on sys.path for universal test execution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import task implementations
from task1_flipkart_agents import SearchAgent, RecommendationAgent, FLIPKART_CATALOG
from task2_spotify_multi_agent_manager import (
    MultiAgentManager as SpotifyManager,
    ChatAgent as SpotifyChatAgent,
    PlaylistAgent as SpotifyPlaylistAgent,
)
from task3_agent_information_sharing import (
    LoggingMultiAgentManager,
    ChatAgent as LoggingChatAgent,
    PlaylistAgent as LoggingPlaylistAgent,
    AgentMessage,
)
from task4_ipl_multi_agent import (
    CricketScoreAgent,
    MatchSummaryAgent,
    IPLMultiAgentSystem,
)


class TestSession20MultiAgentSystems(unittest.TestCase):
    """Test suite for Session 20 multi-agent assignments."""

    # ------------------------------------------------------------------------
    # Task 1 Tests: Independent Flipkart Agents
    # ------------------------------------------------------------------------
    def test_task1_search_agent_matching(self):
        """Test SearchAgent accurately discovers products by query keywords."""
        search_agent = SearchAgent()

        # Query 1: Laptop
        laptop_results = search_agent.search("laptop", max_results=5)
        self.assertGreater(len(laptop_results), 0)
        self.assertTrue(any("ASUS" in p["brand"] or "Apple" in p["brand"] for p in laptop_results))

        # Query 2: Headphones
        audio_results = search_agent.search("headphones", max_results=3)
        self.assertGreater(len(audio_results), 0)
        self.assertEqual(audio_results[0]["brand"], "Sony")

        # Query 3: Non-existent item
        empty_results = search_agent.search("sub-orbital rocket engine 9000")
        self.assertEqual(len(empty_results), 0)

    def test_task1_recommendation_agent_personalization(self):
        """Test RecommendationAgent returns 3 personalized products per user profile."""
        rec_agent = RecommendationAgent()

        # User 101: Gamer / Laptop enthusiast
        recs_101 = rec_agent.get_recommendations("USR-101", count=3)
        self.assertEqual(len(recs_101), 3)
        # Should not recommend already purchased PROD-104
        self.assertFalse(any(p["id"] == "PROD-104" for p in recs_101))

        # User 102: Fitness / Wearables
        recs_102 = rec_agent.get_recommendations("USR-102", count=3)
        self.assertEqual(len(recs_102), 3)
        self.assertTrue(any(p["category"] in ["Wearables", "Audio"] for p in recs_102))

        # Unknown / Guest user fallback
        guest_recs = rec_agent.get_recommendations("USR-UNKNOWN-404", count=3)
        self.assertEqual(len(guest_recs), 3)

    # ------------------------------------------------------------------------
    # Task 2 Tests: Spotify MultiAgentManager
    # ------------------------------------------------------------------------
    def test_task2_spotify_manager_coordination(self):
        """Test MultiAgentManager coordinates ChatAgent and PlaylistAgent delegation."""
        manager = SpotifyManager()
        chat_agent = SpotifyChatAgent()
        playlist_agent = SpotifyPlaylistAgent()

        manager.register_agent("ChatAgent", chat_agent)
        manager.register_agent("PlaylistAgent", playlist_agent)

        self.assertIn("ChatAgent", manager.registry)
        self.assertIn("PlaylistAgent", manager.registry)

        # Conversational query (no delegation needed)
        greeting_resp = manager.handle_user_query("Hi there, who are you?")
        self.assertIn("Spotify AI Assistant", greeting_resp)

        # Playlist request (requires delegation to PlaylistAgent)
        workout_resp = manager.handle_user_query("Create an energetic workout playlist!")
        self.assertIn("Beast Mode High Energy", workout_resp)
        self.assertIn("Till I Collapse", workout_resp)
        self.assertIn("PlaylistAgent", workout_resp)

    # ------------------------------------------------------------------------
    # Task 3 Tests: Information Sharing & Message Logging
    # ------------------------------------------------------------------------
    def test_task3_information_sharing_and_logs(self):
        """Test bi-directional communication, data sharing, and structured audit logs."""
        manager = LoggingMultiAgentManager()
        chat_agent = LoggingChatAgent()
        playlist_agent = LoggingPlaylistAgent()

        manager.register_agent("ChatAgent", chat_agent)
        manager.register_agent("PlaylistAgent", playlist_agent)

        # Message logs should initially be empty
        self.assertEqual(len(manager.message_logs), 0)

        # Request Top Trending Playlist
        response = manager.handle_user_request("Can you give me the top trending playlist?")
        self.assertIn("Top Trending Playlist", response)
        self.assertIn("Espresso", response)
        self.assertIn("Million Dollar Baby", response)

        # Verify message logs captured both the outbound request and inbound response
        logs = manager.message_logs
        self.assertGreaterEqual(len(logs), 2)

        # First message was ChatAgent -> PlaylistAgent (GET_TRENDING_DATA)
        self.assertEqual(logs[0]["from"], "ChatAgent")
        self.assertEqual(logs[0]["to"], "PlaylistAgent")
        self.assertEqual(logs[0]["type"], "GET_TRENDING_DATA")

        # Second message was PlaylistAgent -> ChatAgent (TRENDING_DATA_RESPONSE)
        self.assertEqual(logs[1]["from"], "PlaylistAgent")
        self.assertEqual(logs[1]["to"], "ChatAgent")
        self.assertEqual(logs[1]["type"], "TRENDING_DATA_RESPONSE")
        self.assertIn("tracks", logs[1]["payload"])

    # ------------------------------------------------------------------------
    # Task 4 Tests: IPL Cricket Multi-Agent System
    # ------------------------------------------------------------------------
    def test_task4_cricket_multi_agent_pipeline(self):
        """Test CricketScoreAgent data retrieval and MatchSummaryAgent analytical reporting."""
        system = IPLMultiAgentSystem()

        # Test Completed match
        report_csk_mi = system.process_match("MATCH-2024-01")
        self.assertIn("CHENNAI SUPER KINGS VS MUMBAI INDIANS", report_csk_mi)
        self.assertIn("Chennai Super Kings won by 20 runs", report_csk_mi)
        self.assertIn("Matheesha Pathirana", report_csk_mi)

        # Test Live Chase match with Required Run Rate (RRR)
        report_rcb_kkr = system.process_match("MATCH-2024-02")
        self.assertIn("ROYAL CHALLENGERS BENGALURU VS KOLKATA KNIGHT RIDERS", report_rcb_kkr)
        self.assertIn("Required Run Rate (RRR)", report_rcb_kkr)
        self.assertIn("LIVE_CHASE", report_rcb_kkr)

        # Test Invalid Match ID error handling
        error_report = system.process_match("NON_EXISTENT_MATCH_ID")
        self.assertIn("Error", error_report)
        self.assertIn("not found", error_report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
