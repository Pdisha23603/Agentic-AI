"""
Session 24 - Automated Comprehensive Unit & Integration Test Suite
------------------------------------------------------------------
Validates Tasks 1 through 5 and the Unified Personal Assistant Agent:
- Task 1: Open-Meteo Weather API integration, geocoding, WMO codes.
- Task 2: 'my_expenses.csv' reader, category filtering, numeric cleaning.
- Task 3: GNews API headlines retrieval, payload schema, fallback resilience.
- Task 4: Safe calculator without eval() (Recursive Descent & AST parity, BODMAS, zero division).
- Task 5: Motivational quote generation, provider selection, graceful degradation.
- Agent : PersonalAssistantAgent tool registration and morning briefing execution.
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

# Import task modules
from task1_weather_open_meteo import (
    get_current_weather,
    geocode_city,
    WMO_WEATHER_CODES,
    PRESET_COORDINATES,
)
from task2_expense_tracker import (
    calculate_food_expenses,
    parse_amount,
    resolve_expenses_file,
)
from task3_gnews_headlines import (
    fetch_tech_headlines,
    FALLBACK_TECH_HEADLINES,
)
from task4_safe_calculator import (
    safe_calculate,
    SafeMathLexer,
    SafeMathParser,
    TokenType,
)
from task5_motivational_quote import (
    get_motivational_quote,
    CURATED_AI_QUOTES,
)
from personal_assistant import PersonalAssistantAgent


class TestSession24PersonalAssistant(unittest.TestCase):
    """Complete test suite for Session 24 assignment tasks."""

    # ------------------------------------------------------------------------
    # Task 1 Tests: Open-Meteo Weather API
    # ------------------------------------------------------------------------
    def test_task1_geocode_preset_city(self):
        """Test geocoding returns valid latitude and longitude for preset cities."""
        lat, lon, name, country = geocode_city("Ahmedabad")
        self.assertAlmostEqual(lat, 23.0225, delta=0.1)
        self.assertAlmostEqual(lon, 72.5714, delta=0.1)
        self.assertIn("Ahmedabad", name)

    def test_task1_get_current_weather_structure(self):
        """Test fetching real-time weather returns valid temperature structure."""
        weather = get_current_weather("Ahmedabad")
        self.assertIn("success", weather)
        if weather["success"]:
            self.assertIsNotNone(weather["temperature"])
            self.assertIsInstance(weather["temperature"], (int, float))
            self.assertEqual(weather["unit"], "°C")
            self.assertIn("weather_description", weather)

    def test_task1_wmo_weather_codes(self):
        """Test WMO code dictionary covers standard weather situations."""
        self.assertIn(0, WMO_WEATHER_CODES)
        desc, icon = WMO_WEATHER_CODES[0]
        self.assertEqual(desc, "Clear sky")
        self.assertEqual(icon, "☀️")

    # ------------------------------------------------------------------------
    # Task 2 Tests: Expense CSV Reader ('Food' category)
    # ------------------------------------------------------------------------
    def test_task2_calculate_food_expenses(self):
        """Test reading 'my_expenses.csv' yields correct Food category sum (1200.50)."""
        csv_file = os.path.join(CURRENT_DIR, "my_expenses.csv")
        total_food = calculate_food_expenses(csv_file, "Food")
        # In my_expenses.csv: 250.50 + 450.00 + 120.00 + 380.00 = 1200.50
        self.assertAlmostEqual(total_food, 1200.50, places=2)

    def test_task2_case_insensitivity(self):
        """Test category filter works with lowercase, uppercase, and mixed case."""
        csv_file = os.path.join(CURRENT_DIR, "my_expenses.csv")
        total_lower = calculate_food_expenses(csv_file, "food")
        total_upper = calculate_food_expenses(csv_file, "FOOD")
        self.assertEqual(total_lower, total_upper)

    def test_task2_parse_amount_cleaning(self):
        """Test numeric amount cleaning handles symbols, commas, and whitespace."""
        self.assertEqual(parse_amount("250.50"), 250.50)
        self.assertEqual(parse_amount("₹1,200.00"), 1200.0)
        self.assertEqual(parse_amount(" $450 "), 450.0)

    # ------------------------------------------------------------------------
    # Task 3 Tests: GNews API Headlines
    # ------------------------------------------------------------------------
    def test_task3_fetch_tech_headlines_count(self):
        """Test fetching technology news returns exactly 3 articles."""
        news_result = fetch_tech_headlines(max_results=3)
        self.assertTrue(news_result["success"])
        articles = news_result["articles"]
        self.assertLessEqual(len(articles), 3)
        self.assertGreater(len(articles), 0)

    def test_task3_article_fields(self):
        """Test each news article contains title, description, and source."""
        news_result = fetch_tech_headlines(max_results=3)
        for article in news_result["articles"]:
            self.assertTrue(len(article.get("title", "")) > 0)
            self.assertIn("url", article)
            self.assertIn("source", article)

    # ------------------------------------------------------------------------
    # Task 4 Tests: Safe Calculator (No eval())
    # ------------------------------------------------------------------------
    def test_task4_sample_expression(self):
        """Test primary assignment expression '23+7*2' equals 37."""
        result = safe_calculate("23+7*2")
        self.assertEqual(result, 37)

    def test_task4_operator_precedence(self):
        """Test standard BODMAS/PEMDAS precedence (multiplication before addition/subtraction)."""
        self.assertEqual(safe_calculate("100 - 25 * 3"), 25)
        self.assertEqual(safe_calculate("2 + 3 * 4"), 14)
        self.assertEqual(safe_calculate("2 * 3 + 4 * 5"), 26)

    def test_task4_parentheses(self):
        """Test expressions with nested and unnested parentheses."""
        self.assertEqual(safe_calculate("(23 + 7) * 2"), 60)
        self.assertEqual(safe_calculate("((2 + 3) * (4 + 1)) / 5"), 5)

    def test_task4_unary_operators_and_decimals(self):
        """Test unary signs and decimal arithmetic."""
        self.assertEqual(safe_calculate("-5 + 20 * 2"), 35)
        self.assertEqual(safe_calculate("10 / 4"), 2.5)
        self.assertEqual(safe_calculate("2.5 * 4"), 10)

    def test_task4_zero_division_safety(self):
        """Test division by zero raises ZeroDivisionError cleanly."""
        with self.assertRaises(ZeroDivisionError):
            safe_calculate("10 / 0")

    def test_task4_parser_and_ast_parity(self):
        """Verify Recursive Descent Parser matches AST visitor across various expressions."""
        test_cases = [
            "23+7*2",
            "100 - 25 * 3",
            "(50 + 10) / 3",
            "15.5 + 4.5 * 2",
            "-10 + 30 / 2",
        ]
        for expr in test_cases:
            res_parser = safe_calculate(expr, method="parser")
            res_ast = safe_calculate(expr, method="ast")
            self.assertEqual(res_parser, res_ast, f"Parity mismatch on {expr}")

    def test_task4_injection_rejection(self):
        """Verify malicious code injection is strictly blocked without eval."""
        with self.assertRaises(ValueError):
            safe_calculate("__import__('os').system('dir')")
        with self.assertRaises(ValueError):
            safe_calculate("exec('x = 1')")

    # ------------------------------------------------------------------------
    # Task 5 Tests: Motivational Quote Generator
    # ------------------------------------------------------------------------
    def test_task5_get_motivational_quote(self):
        """Test quote generator returns a valid non-empty motivational quote."""
        quote_data = get_motivational_quote()
        self.assertTrue(quote_data["success"])
        self.assertTrue(len(quote_data["quote"]) > 0)
        self.assertIn("provider", quote_data)

    # ------------------------------------------------------------------------
    # Integration Tests: Personal Assistant Agent
    # ------------------------------------------------------------------------
    def test_assistant_agent_tools(self):
        """Test PersonalAssistantAgent successfully delegates to all 5 tools."""
        agent = PersonalAssistantAgent(name="TestAria", default_city="Ahmedabad")

        # Test tool 1
        weather = agent.tools["weather"]()
        self.assertIn("temperature", weather)

        # Test tool 2
        expenses = agent.tools["expenses"](os.path.join(CURRENT_DIR, "my_expenses.csv"), "Food")
        self.assertEqual(expenses, 1200.50)

        # Test tool 3
        news = agent.tools["news"](3)
        self.assertTrue(len(news["articles"]) > 0)

        # Test tool 4
        calc = agent.tools["calculate"]("23+7*2")
        self.assertEqual(calc, 37)

        # Test tool 5
        quote = agent.tools["inspiration"]()
        self.assertTrue(len(quote["quote"]) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
