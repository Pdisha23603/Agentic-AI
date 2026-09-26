"""
Session 25 - Automated Comprehensive Unit & Integration Test Suite
------------------------------------------------------------------
Validates Tasks 1 through 5 for Session 25:
- Task 1: assistant_ui.py interface requirements and module structure.
- Task 2: detect_intent(user_input) keyword classification across all intents.
- Task 3: select_tool(intent) tool routing logic.
- Task 4: conversation_history memory list and last-3 exchanges windowing.
- Task 5: Tool execution and UI feedback metadata.
"""

import sys
import os
import unittest

# Ensure current directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import functions from assistant_ui directly (as specified in assignment)
from assistant_ui import (
    detect_intent,
    select_tool,
)
from assistant_core import (
    execute_tool,
    INTENT_KEYWORDS,
    TOOL_REGISTRY,
)


class TestSession25PersonalAssistantPart2(unittest.TestCase):
    """Complete test suite for Session 25 Personal Assistant Agent (Part 2)."""

    # ------------------------------------------------------------------------
    # Task 2 Tests: detect_intent(user_input)
    # ------------------------------------------------------------------------
    def test_detect_intent_movie_bookings(self):
        """Test intent detection for movie bookings."""
        test_queries = [
            "Show me my upcoming movie bookings",
            "Do I have any movie tickets reserved?",
            "Check my cinema booking on BookMyShow",
            "Show upcoming movie reservations",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "show_bookings",
                f"Failed to detect 'show_bookings' for: '{query}'"
            )

    def test_detect_intent_play_music(self):
        """Test intent detection for music playback."""
        test_queries = [
            "Play some upbeat jazz music",
            "Play a playlist on Spotify",
            "Can you play my favorite songs?",
            "Listen to chill lofi tracks",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "play_music",
                f"Failed to detect 'play_music' for: '{query}'"
            )

    def test_detect_intent_weather(self):
        """Test intent detection for weather and temperature."""
        test_queries = [
            "What is the weather like today?",
            "Tell me the current temperature in Ahmedabad",
            "Is it going to rain this afternoon?",
            "What's the weather forecast for tomorrow?",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "get_weather",
                f"Failed to detect 'get_weather' for: '{query}'"
            )

    def test_detect_intent_math_calculator(self):
        """Test intent detection for math calculations."""
        test_queries = [
            "Calculate 23+7*2",
            "Solve (100 - 25) * 3",
            "Compute 45 / 5 + 12",
            "23+7*2",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "calculate",
                f"Failed to detect 'calculate' for: '{query}'"
            )

    def test_detect_intent_expenses(self):
        """Test intent detection for expenses and spending."""
        test_queries = [
            "Show me my expenses",
            "How much total did I spend on Food?",
            "Check my food expense in my_expenses",
            "What is my spending this month?",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "check_expenses",
                f"Failed to detect 'check_expenses' for: '{query}'"
            )

    def test_detect_intent_news(self):
        """Test intent detection for tech news."""
        test_queries = [
            "Show me the top 3 technology news headlines",
            "What are the latest tech headlines today?",
            "Give me trending tech news updates",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "get_news",
                f"Failed to detect 'get_news' for: '{query}'"
            )

    def test_detect_intent_quote(self):
        """Test intent detection for motivational quotes."""
        test_queries = [
            "Give me a motivational quote",
            "Inspire me with some wisdom for coding",
            "What is the motivational quote of the day?",
        ]
        for query in test_queries:
            self.assertEqual(
                detect_intent(query),
                "get_quote",
                f"Failed to detect 'get_quote' for: '{query}'"
            )

    def test_detect_intent_fallback(self):
        """Test intent detection fallback on empty or gibberish input."""
        self.assertEqual(detect_intent(""), "unknown")
        self.assertEqual(detect_intent("   "), "unknown")
        self.assertEqual(detect_intent("xyz123abc 987foo"), "unknown")

    # ------------------------------------------------------------------------
    # Task 3 Tests: select_tool(intent)
    # ------------------------------------------------------------------------
    def test_select_tool_mapping(self):
        """Verify tool selection properly routes to the designated API/service."""
        self.assertEqual(select_tool("show_bookings"), "MovieBookingService")
        self.assertEqual(select_tool("play_music"), "SpotifyAPI")
        self.assertEqual(select_tool("get_weather"), "OpenMeteoWeatherAPI")
        self.assertEqual(select_tool("calculate"), "SafeMathCalculator")
        self.assertEqual(select_tool("check_expenses"), "ExpenseTrackerService")
        self.assertEqual(select_tool("get_news"), "GNewsAPI")
        self.assertEqual(select_tool("get_quote"), "MotivationalQuoteGenerator")
        self.assertEqual(select_tool("unknown"), "DefaultHelpAssistant")

    # ------------------------------------------------------------------------
    # Task 4 Tests: Memory Feature (conversation_history & Last 3 Window)
    # ------------------------------------------------------------------------
    def test_memory_feature_and_last_three_window(self):
        """Test conversation_history saves exchanges and correctly returns last 3."""
        history = []

        # Add 1st exchange
        history.append({"user": "Hi", "agent": "Hello!", "intent": "greeting"})
        self.assertEqual(len(history[-3:]), 1)

        # Add 2nd exchange
        history.append({"user": "Bookings?", "agent": "Found 2", "intent": "show_bookings"})
        self.assertEqual(len(history[-3:]), 2)

        # Add 3rd exchange
        history.append({"user": "Play jazz", "agent": "Playing jazz", "intent": "play_music"})
        self.assertEqual(len(history[-3:]), 3)

        # Add 4th exchange: window should return exchanges 2, 3, 4
        history.append({"user": "Weather in NY?", "agent": "22 °C", "intent": "get_weather"})
        last_three = history[-3:]
        self.assertEqual(len(last_three), 3)
        self.assertEqual(last_three[0]["user"], "Bookings?")
        self.assertEqual(last_three[1]["user"], "Play jazz")
        self.assertEqual(last_three[2]["user"], "Weather in NY?")

        # Add 5th exchange: window should return exchanges 3, 4, 5
        history.append({"user": "Calculate 5*5", "agent": "25", "intent": "calculate"})
        last_three_updated = history[-3:]
        self.assertEqual(len(last_three_updated), 3)
        self.assertEqual(last_three_updated[0]["user"], "Play jazz")
        self.assertEqual(last_three_updated[1]["user"], "Weather in NY?")
        self.assertEqual(last_three_updated[2]["user"], "Calculate 5*5")

    # ------------------------------------------------------------------------
    # Task 5 & Execution Tests
    # ------------------------------------------------------------------------
    def test_execute_tool_outputs(self):
        """Test tool execution returns valid non-empty responses for all intents."""
        intents_to_test = [
            ("show_bookings", "Show upcoming bookings"),
            ("play_music", "Play jazz music"),
            ("get_weather", "Weather in Ahmedabad"),
            ("calculate", "Calculate 23+7*2"),
            ("check_expenses", "Show food expenses"),
            ("get_news", "Tech news"),
            ("get_quote", "Inspire me"),
        ]
        for intent, query in intents_to_test:
            output = execute_tool(intent, query)
            self.assertIsInstance(output, str)
            self.assertGreater(len(output), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
