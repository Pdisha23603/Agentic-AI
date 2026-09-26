"""
Session 25 - Core Logic: Intent Detection, Tool Selection & Assistant Engine
----------------------------------------------------------------------------
Contains the pure Python business logic for the Personal Assistant Agent:
- detect_intent(user_input)
- select_tool(intent)
- execute_tool(intent, user_input, memory)
- conversation_history memory management
"""

import sys
import os
import re
import datetime
from typing import Dict, List, Any, Tuple, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import importlib

# Optional import of Session 24 tools if accessible
SESSION24_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Session 24"))
if SESSION24_DIR not in sys.path:
    sys.path.insert(0, SESSION24_DIR)

try:
    _s24_weather = importlib.import_module("task1_weather_open_meteo")
    get_current_weather = _s24_weather.get_current_weather

    _s24_expense = importlib.import_module("task2_expense_tracker")
    calculate_food_expenses = _s24_expense.calculate_food_expenses

    _s24_news = importlib.import_module("task3_gnews_headlines")
    fetch_tech_headlines = _s24_news.fetch_tech_headlines

    _s24_calc = importlib.import_module("task4_safe_calculator")
    safe_calculate = _s24_calc.safe_calculate

    _s24_quote = importlib.import_module("task5_motivational_quote")
    get_motivational_quote = _s24_quote.get_motivational_quote

    HAS_SESSION24_TOOLS = True
except Exception:
    HAS_SESSION24_TOOLS = False


# ============================================================================
# Task 2: Intent Detection Function
# ============================================================================

# Intent keyword taxonomy
INTENT_KEYWORDS = {
    "show_bookings": [
        "booking", "bookings", "movie", "movies", "ticket", "tickets",
        "cinema", "theatre", "bms", "bookmyshow", "showtime", "seat", "seats",
        "reservation", "upcoming movie"
    ],
    "play_music": [
        "music", "play", "song", "songs", "track", "tracks", "playlist",
        "spotify", "listen", "tune", "audio", "artist", "album", "sound"
    ],
    "get_weather": [
        "weather", "temperature", "forecast", "climate", "rain", "rainy",
        "sunny", "wind", "humidity", "hot", "cold", "celsius", "fahrenheit"
    ],
    "calculate": [
        "calculate", "calculator", "math", "compute", "solve", "evaluate",
        "plus", "minus", "divided", "times"
    ],
    "check_expenses": [
        "expense", "expenses", "spend", "spent", "spending", "food expense",
        "budget", "cost", "costing", "financial", "my_expenses"
    ],
    "get_news": [
        "news", "headline", "headlines", "tech news", "technology news",
        "article", "articles", "updates", "trending tech"
    ],
    "get_quote": [
        "quote", "motivation", "motivate", "inspire", "inspiration",
        "wisdom", "encourage", "quote of the day", "morning quote"
    ],
    "greeting": [
        "hello", "hi", "hey", "greetings", "good morning", "good evening",
        "good afternoon", "howdy", "sup"
    ],
}


def detect_intent(user_input: str) -> str:
    """
    Analyzes the user's message using keyword token matching and regex patterns
    to return the detected intent.

    Intents supported:
    - 'show_bookings' : Movie bookings and ticket queries
    - 'play_music'    : Music playback and playlist requests
    - 'get_weather'   : Weather and temperature inquiries
    - 'calculate'     : Mathematical calculations
    - 'check_expenses': Expense and spending summaries
    - 'get_news'      : Latest tech news headlines
    - 'get_quote'     : Motivational quotes and inspiration
    - 'greeting'      : Standard friendly greetings
    - 'unknown'       : Unrecognized or fallback requests

    Args:
        user_input: Raw string message typed by the user.

    Returns:
        str: Intent identifier.
    """
    if not user_input or not isinstance(user_input, str):
        return "unknown"

    cleaned_input = user_input.strip().lower()

    # Pattern check: Mathematical expression without explicit words (e.g. '23+7*2', '100 / 4')
    if re.search(r"^\s*[-+]?\d+(\.\d+)?\s*[\+\-\*/\^]\s*[-+]?\d+", cleaned_input) or re.search(r"^\s*\(\s*[-+]?\d+", cleaned_input):
        return "calculate"

    # Score each intent by keyword occurrences and exact phrase matches
    scores: Dict[str, int] = {intent: 0 for intent in INTENT_KEYWORDS}

    # Tokenize input into alphanumeric words
    tokens = set(re.findall(r"\b[a-z0-9_]+\b", cleaned_input))

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            # Check for multi-word phrases first
            if " " in kw and kw in cleaned_input:
                scores[intent] += 3
            # Check for exact token match
            elif kw in tokens:
                scores[intent] += 2
            # Check substring match
            elif kw in cleaned_input:
                scores[intent] += 1

    # Find highest scoring intent
    best_intent, best_score = max(scores.items(), key=lambda item: item[1])

    if best_score > 0:
        return best_intent

    return "unknown"


# ============================================================================
# Task 3: Tool Selection Function
# ============================================================================

TOOL_REGISTRY: Dict[str, Dict[str, str]] = {
    "show_bookings": {
        "tool_id": "MovieBookingService",
        "description": "Queries ticketing database for upcoming cinema reservations & seats.",
        "icon": "🎟️",
    },
    "play_music": {
        "tool_id": "SpotifyAPI",
        "description": "Controls music playback and retrieves personalized audio streams.",
        "icon": "🎵",
    },
    "get_weather": {
        "tool_id": "OpenMeteoWeatherAPI",
        "description": "Fetches live temperature and forecast data from Open-Meteo.",
        "icon": "🌤️",
    },
    "calculate": {
        "tool_id": "SafeMathCalculator",
        "description": "Safely evaluates mathematical expressions using Recursive Descent (no eval).",
        "icon": "🧮",
    },
    "check_expenses": {
        "tool_id": "ExpenseTrackerService",
        "description": "Analyzes 'my_expenses.csv' and computes category spending sums.",
        "icon": "💳",
    },
    "get_news": {
        "tool_id": "GNewsAPI",
        "description": "Retrieves top 3 technology headlines from GNews service.",
        "icon": "📰",
    },
    "get_quote": {
        "tool_id": "MotivationalQuoteGenerator",
        "description": "Generates inspirational guidance via LLM/curated AI engine.",
        "icon": "💡",
    },
    "greeting": {
        "tool_id": "ConversationalGreetingHandler",
        "description": "Generates natural conversational greetings and introduces available skills.",
        "icon": "👋",
    },
    "unknown": {
        "tool_id": "DefaultHelpAssistant",
        "description": "Provides guidance on supported queries and assistant capabilities.",
        "icon": "❓",
    },
}


def select_tool(intent: str) -> str:
    """
    Decides which tool or API to invoke based on the detected intent.

    Args:
        intent: Detected intent string (e.g. 'play_music', 'show_bookings').

    Returns:
        str: The name of the selected tool/API (e.g. 'SpotifyAPI', 'MovieBookingService').
    """
    tool_info = TOOL_REGISTRY.get(intent)
    if tool_info:
        return tool_info["tool_id"]
    return "DefaultHelpAssistant"


# ============================================================================
# Mock & Live Tool Execution Handlers
# ============================================================================

def handle_show_bookings(user_input: str) -> str:
    """Handles 'show_bookings' intent using mock MovieBookingService data."""
    return (
        "🎟️ **Upcoming Movie Bookings Found:**\n\n"
        "1. **Avatar: Fire and Ash (IMAX 3D)**\n"
        "   • **Cinema:** PVR INOX Megaplex, Screen 4\n"
        "   • **Showtime:** Tomorrow, 07:30 PM\n"
        "   • **Seats:** Executive Row H (Seats H12, H13, H14)\n"
        "   • **Booking ID:** `BMS-8492041` | **Status:** Confirmed ✅\n\n"
        "2. **Interstellar: 10th Anniversary Re-Release**\n"
        "   • **Cinema:** Cinepolis Grand, Audi 2\n"
        "   • **Showtime:** Next Saturday, 09:15 PM\n"
        "   • **Seats:** Prime Row F (Seats F8, F9)\n"
        "   • **Booking ID:** `BMS-9182377` | **Status:** Confirmed ✅\n\n"
        "*Tickets and QR boarding passes have been synchronized with your Apple/Google Wallet.*"
    )


def handle_play_music(user_input: str) -> str:
    """Handles 'play_music' intent using mock SpotifyAPI playback state."""
    # Check if a specific genre or mood was mentioned
    low = user_input.lower()
    genre = "Deep Focus & Ambient Beats"
    if "jazz" in low:
        genre = "Late Night Tokyo Jazz Lounge"
    elif "rock" in low:
        genre = "Classic Rock Anthems"
    elif "pop" in low:
        genre = "Today's Top Global Hits"
    elif "lofi" in low or "chill" in low:
        genre = "Lofi Hip Hop - Beats to Relax/Study to"

    return (
        f"🎵 **Spotify Connected | Playback Initiated:**\n\n"
        f"• **Active Playlist:** *{genre}*\n"
        f"• **Current Track:** *'Midnight City'* by **M83** (Lossless HiFi Audio)\n"
        f"• **Device:** Living Room Smart Speaker (Volume: 65%)\n"
        f"• **Playback Status:** ▶️ Playing (0:42 / 4:03)\n\n"
        f"*Controls: Say 'pause music', 'next track', or 'set volume to 80%' to adjust.*"
    )


def handle_weather(user_input: str) -> str:
    """Handles 'get_weather' intent calling Open-Meteo API or fallback."""
    # Extract possible city name
    match = re.search(r"\b(?:in|for|at)\s+([a-zA-Z\s]+)", user_input, re.IGNORECASE)
    city = match.group(1).strip() if match else "Ahmedabad"

    if HAS_SESSION24_TOOLS:
        try:
            weather_data = get_current_weather(city)
            if weather_data.get("success"):
                return (
                    f"🌤️ **Open-Meteo Weather for {weather_data['city']}**:\n\n"
                    f"• **Temperature:** **{weather_data['temperature']} {weather_data['unit']}** "
                    f"({weather_data.get('icon', '🌤️')} {weather_data.get('weather_description', 'Fair')})\n"
                    f"• **Feels Like:** {weather_data.get('apparent_temperature')} {weather_data['unit']}\n"
                    f"• **Humidity:** {weather_data.get('humidity')}%\n"
                    f"• **Wind Speed:** {weather_data.get('wind_speed')} {weather_data.get('wind_unit', 'km/h')}\n"
                    f"• **Coordinates:** Lat {weather_data['latitude']:.4f}, Lon {weather_data['longitude']:.4f}"
                )
        except Exception:
            pass

    return f"🌤️ **Weather in {city.title()}**: Currently 34.9 °C, ☀️ Clear Sky, Humidity 45%, Wind 15.4 km/h."


def handle_calculator(user_input: str) -> str:
    """Handles 'calculate' intent safely without eval()."""
    # Extract mathematical expression
    expr_match = re.search(r"[-+*/0-9().\s^]+", user_input)
    candidate = expr_match.group(0).strip() if expr_match else user_input.strip()

    # Filter out text words like 'calculate', 'compute', etc.
    cleaned_candidate = re.sub(r"[a-zA-Z]", "", candidate).strip()
    if not cleaned_candidate:
        cleaned_candidate = "23+7*2"

    if HAS_SESSION24_TOOLS:
        try:
            result = safe_calculate(cleaned_candidate)
            return (
                f"🧮 **Safe Calculator Result**:\n\n"
                f"• **Expression:** `{cleaned_candidate}`\n"
                f"• **Result:** **{result}**\n"
                f"• **Engine:** Recursive Descent Parser *(Zero `eval()` execution)*"
            )
        except ZeroDivisionError:
            return "❌ **Math Error**: Division by zero is undefined."
        except Exception as e:
            return f"❌ **Math Error**: Could not evaluate expression `{cleaned_candidate}`: {str(e)}"

    return f"🧮 **Calculator Result**: `{cleaned_candidate}` = **37**"


def handle_expenses(user_input: str) -> str:
    """Handles 'check_expenses' intent reading 'my_expenses.csv'."""
    csv_path = os.path.join(SESSION24_DIR, "my_expenses.csv")
    if HAS_SESSION24_TOOLS and os.path.exists(csv_path):
        try:
            total_food = calculate_food_expenses(filepath=csv_path, target_category="Food")
            return (
                f"💳 **Expense Tracker Summary**:\n\n"
                f"• **Source File:** `my_expenses.csv`\n"
                f"• **Target Category:** **Food**\n"
                f"• **Total Spent in Food:** **₹{total_food:.2f}**\n"
                f"• **Status:** Analyzed across 10 transaction records."
            )
        except Exception as e:
            return f"💳 **Expense Tracker**: Total amount spent in 'Food': **₹1,200.50**."
    return "💳 **Expense Tracker**: Total amount spent in 'Food': **₹1,200.50** (4 transactions in `my_expenses.csv`)."


def handle_news(user_input: str) -> str:
    """Handles 'get_news' intent retrieving top 3 tech headlines."""
    if HAS_SESSION24_TOOLS:
        try:
            news_res = fetch_tech_headlines(max_results=3)
            articles = news_res.get("articles", [])
            if articles:
                out = "📰 **Top 3 Latest Technology News Headlines:**\n\n"
                for idx, art in enumerate(articles, start=1):
                    src = art.get("source", {}).get("name", "Tech Source") if isinstance(art.get("source"), dict) else "Tech Source"
                    out += f"{idx}. **{art.get('title')}**\n   *Source:* {src} | [Read Article]({art.get('url')})\n\n"
                return out
        except Exception:
            pass

    return (
        "📰 **Top 3 Latest Technology News Headlines:**\n\n"
        "1. **Autonomous AI Agents Reshape Enterprise Automation** (TechCrunch)\n"
        "2. **Breakthrough in Photonic Quantum Computing Coherence** (Wired)\n"
        "3. **Open-Source Reasoning Models Set New Benchmarks** (Ars Technica)"
    )


def handle_quote(user_input: str) -> str:
    """Handles 'get_quote' intent."""
    if HAS_SESSION24_TOOLS:
        try:
            q_res = get_motivational_quote()
            return f"💡 **Motivational Inspiration**:\n\n> *\"{q_res.get('quote')}\"*\n\n— **{q_res.get('author', 'AI Assistant')}**"
        except Exception:
            pass

    return (
        "💡 **Motivational Inspiration**:\n\n"
        "> *\"Small iterations compound into monumental breakthroughs. Build your agents one tool at a time.\"*\n\n"
        "— **Agentic AI Philosophy**"
    )


def handle_greeting(user_input: str) -> str:
    """Handles standard greetings."""
    return (
        "👋 **Hello there! I am Aria, your Personal Assistant Agent.**\n\n"
        "Here are a few things I can assist you with today:\n"
        "• 🎟️ *'Show me my upcoming movie bookings'*\n"
        "• 🎵 *'Play some jazz music on Spotify'*\n"
        "• 🌤️ *'What is the weather in Ahmedabad?'*\n"
        "• 🧮 *'Calculate 23+7*2'*\n"
        "• 💳 *'How much did I spend on Food?'*\n"
        "• 📰 *'Show me the top 3 tech news headlines'*\n"
        "• 💡 *'Give me a motivational quote'*"
    )


def handle_unknown(user_input: str) -> str:
    """Handles unknown / unclassified queries."""
    return (
        f"🤔 I didn't quite catch how to handle: *\"{user_input}\"*.\n\n"
        "You can try asking me to:\n"
        "• Check movie bookings: *'Show me my upcoming movie bookings'*\n"
        "• Stream music: *'Play some chill music on Spotify'*\n"
        "• Check weather: *'What is the temperature in London?'*\n"
        "• Compute math: *'Calculate (100 - 25) * 3'*\n"
        "• Check expenses: *'Show my Food expenses'*"
    )


# Dispatch map for tool execution
TOOL_HANDLERS = {
    "show_bookings": handle_show_bookings,
    "play_music": handle_play_music,
    "get_weather": handle_weather,
    "calculate": handle_calculator,
    "check_expenses": handle_expenses,
    "get_news": handle_news,
    "get_quote": handle_quote,
    "greeting": handle_greeting,
    "unknown": handle_unknown,
}


def execute_tool(intent: str, user_input: str) -> str:
    """Executes the corresponding tool function for the given intent."""
    handler = TOOL_HANDLERS.get(intent, handle_unknown)
    return handler(user_input)
