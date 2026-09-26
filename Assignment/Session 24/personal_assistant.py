"""
Session 24 - Case Study: Building a Personal Assistant Agent (Part 1)
---------------------------------------------------------------------
Unified Personal Assistant Agent orchestrating five specialized capabilities:
1. Weather Tool         : Live temperature & weather conditions via Open-Meteo API
2. Expense Analyzer Tool: CSV expense aggregation and category tracking ('Food')
3. Tech News Tool       : Top 3 technology headlines via GNews API
4. Calculator Tool      : Safe math evaluator (no eval()) supporting +, -, *, /
5. Inspiration Tool     : Short motivational quote generation via Gemini/OpenAI API

This script demonstrates modular tool-calling, centralized telemetry,
defensive fallbacks, and a complete 'Morning Briefing' routine.
"""

import sys
import os
from typing import Dict, Any, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure local directory is on path for tool imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import individual task modules
from task1_weather_open_meteo import get_current_weather, display_weather_report
from task2_expense_tracker import calculate_food_expenses
from task3_gnews_headlines import fetch_tech_headlines, display_tech_headlines
from task4_safe_calculator import safe_calculate
from task5_motivational_quote import get_motivational_quote, display_quote


class PersonalAssistantAgent:
    """
    Intelligent Personal Assistant Agent that orchestrates external APIs,
    local file analytics, and safe computation tools.
    """

    def __init__(self, name: str = "Aria", user_name: str = "Developer", default_city: str = "Ahmedabad"):
        self.name = name
        self.user_name = user_name
        self.default_city = default_city
        self.tools = {
            "weather": self.get_weather,
            "expenses": self.get_food_expenses,
            "news": self.get_tech_news,
            "calculate": self.calculate,
            "inspiration": self.get_inspiration,
        }

    # ------------------------------------------------------------------------
    # Tool 1: Weather Check (Open-Meteo API)
    # ------------------------------------------------------------------------
    def get_weather(self, city: Optional[str] = None) -> Dict[str, Any]:
        """Tool 1: Fetches real-time temperature and conditions for target city."""
        target_city = city or self.default_city
        print(f"\n[{self.name} Agent 🌤️] Fetching current weather for '{target_city}'...")
        return get_current_weather(target_city)

    # ------------------------------------------------------------------------
    # Tool 2: Expense Analyzer ('Food' category in my_expenses.csv)
    # ------------------------------------------------------------------------
    def get_food_expenses(self, csv_file: str = "my_expenses.csv", category: str = "Food") -> float:
        """Tool 2: Computes total expenses in the specified category from CSV."""
        print(f"\n[{self.name} Agent 💳] Calculating spending for category '{category}' in '{csv_file}'...")
        return calculate_food_expenses(filepath=csv_file, target_category=category)

    # ------------------------------------------------------------------------
    # Tool 3: Latest Tech Headlines (GNews API)
    # ------------------------------------------------------------------------
    def get_tech_news(self, max_items: int = 3) -> Dict[str, Any]:
        """Tool 3: Fetches top 3 latest technology headlines."""
        print(f"\n[{self.name} Agent 📰] Fetching top {max_items} technology news headlines...")
        return fetch_tech_headlines(max_results=max_items)

    # ------------------------------------------------------------------------
    # Tool 4: Safe Expression Calculator (No eval)
    # ------------------------------------------------------------------------
    def calculate(self, expression: str) -> Any:
        """Tool 4: Evaluates mathematical expressions safely without eval()."""
        print(f"\n[{self.name} Agent 🧮] Safely computing mathematical expression: '{expression}'...")
        return safe_calculate(expression)

    # ------------------------------------------------------------------------
    # Tool 5: Daily Motivation Quote (Gemini / OpenAI API)
    # ------------------------------------------------------------------------
    def get_inspiration(self) -> Dict[str, Any]:
        """Tool 5: Generates a short motivational quote."""
        print(f"\n[{self.name} Agent 💡] Retrieving daily motivational inspiration...")
        return get_motivational_quote()

    # ------------------------------------------------------------------------
    # Autonomous Workflow: Complete Morning Briefing
    # ------------------------------------------------------------------------
    def run_morning_briefing(self, city: Optional[str] = None):
        """
        Executes a comprehensive morning briefing coordinating all 5 agent tools.
        """
        target_city = city or self.default_city
        print("\n" + "=" * 70)
        print(f" 🤖  GOOD MORNING, {self.user_name.upper()}! HERE IS YOUR DAILY BRIEFING")
        print(f"     Personal Assistant: {self.name} | City: {target_city}")
        print("=" * 70)

        # 1. Weather Briefing
        weather_data = self.get_weather(target_city)
        if weather_data.get("success"):
            print(f"🌤️  Weather in {weather_data['city']}: {weather_data['temperature']} {weather_data['unit']} "
                  f"({weather_data.get('icon', '')} {weather_data.get('weather_description', '')})")
            print(f"    Feels like: {weather_data.get('apparent_temperature')} {weather_data['unit']} | "
                  f"Humidity: {weather_data.get('humidity')}% | Wind: {weather_data.get('wind_speed')} {weather_data.get('wind_unit')}")
        else:
            print(f"⚠️  Weather info unavailable: {weather_data.get('error')}")

        print("-" * 70)

        # 2. Daily Motivational Quote
        quote_data = self.get_inspiration()
        print(f"💡  Quote of the Day:\n    \"{quote_data.get('quote')}\"")
        if quote_data.get("author"):
            print(f"    — {quote_data.get('author')}")
        print(f"    (Source: {quote_data.get('provider')})")

        print("-" * 70)

        # 3. Expense Tracker Snapshot
        food_total = self.get_food_expenses("my_expenses.csv", "Food")

        print("-" * 70)

        # 4. Tech News Headlines
        news_data = self.get_tech_news(max_items=3)
        print("📰  Top 3 Technology Headlines:")
        for idx, item in enumerate(news_data.get("articles", []), start=1):
            source_info = item.get("source", {})
            src = source_info.get("name") if isinstance(source_info, dict) else str(source_info)
            print(f"    [{idx}] {item.get('title')} ({src or 'Tech'})")

        print("-" * 70)

        # 5. Calculator Demonstration
        sample_expr = "23+7*2"
        calc_result = self.calculate(sample_expr)
        print(f"🧮  Calculator Check: '{sample_expr}' = {calc_result} (Computed safely without eval())")

        print("=" * 70)
        print(f" ✅  Briefing Complete. {self.name} is ready for instructions.\n" + "=" * 70)


def main():
    """Main execution point demonstrating the personal assistant agent."""
    city_arg = sys.argv[1] if len(sys.argv) > 1 else "Ahmedabad"
    assistant = PersonalAssistantAgent(name="Aria", user_name="Student", default_city=city_arg)
    assistant.run_morning_briefing()


if __name__ == "__main__":
    main()
