"""
Session 25 - Case Study: Building a Personal Assistant Agent (Part 2)
---------------------------------------------------------------------
Interactive Streamlit UI for the Personal Assistant Agent.

Tasks Implemented:
1. Streamlit chat interface where users type a request and see agent responses.
2. detect_intent(user_input): Intent classification function with keyword matching.
3. select_tool(intent): Tool/API routing logic based on detected intent.
4. Memory feature: conversation_history list storing exchanges, showing last 3 exchanges.
5. UI feedback: st.spinner and st.info displaying gathering/executing state transitions.
"""

import sys
import os
import time
import re
import datetime
from typing import Dict, List, Any, Optional

import streamlit as st

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure local directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import helper handlers from assistant_core
try:
    from assistant_core import (
        INTENT_KEYWORDS,
        TOOL_REGISTRY,
        execute_tool,
        detect_intent as core_detect_intent,
        select_tool as core_select_tool,
    )
except ImportError:
    INTENT_KEYWORDS = {
        "show_bookings": ["booking", "bookings", "movie", "ticket", "tickets", "cinema", "bms", "seat"],
        "play_music": ["music", "song", "play", "track", "playlist", "spotify", "listen"],
        "get_weather": ["weather", "temperature", "forecast", "climate", "rain"],
        "calculate": ["calculate", "math", "compute", "solve", "+", "-", "*", "/"],
        "check_expenses": ["expense", "expenses", "food expense", "spent", "budget"],
        "get_news": ["news", "headline", "headlines", "tech news"],
        "get_quote": ["quote", "motivation", "motivate", "inspire", "inspiration"],
    }
    TOOL_REGISTRY = {
        "show_bookings": {"tool_id": "MovieBookingService", "description": "Cinema bookings & seats", "icon": "🎟️"},
        "play_music": {"tool_id": "SpotifyAPI", "description": "Music streaming & playback", "icon": "🎵"},
        "get_weather": {"tool_id": "OpenMeteoWeatherAPI", "description": "Real-time weather forecast", "icon": "🌤️"},
        "calculate": {"tool_id": "SafeMathCalculator", "description": "Safe math parser without eval", "icon": "🧮"},
        "check_expenses": {"tool_id": "ExpenseTrackerService", "description": "Reads my_expenses.csv", "icon": "💳"},
        "get_news": {"tool_id": "GNewsAPI", "description": "Top 3 technology headlines", "icon": "📰"},
        "get_quote": {"tool_id": "MotivationalQuoteGenerator", "description": "AI motivational quotes", "icon": "💡"},
    }
    def core_detect_intent(user_input: str) -> str:
        low = user_input.lower()
        if any(w in low for w in INTENT_KEYWORDS["show_bookings"]): return "show_bookings"
        if any(w in low for w in INTENT_KEYWORDS["play_music"]): return "play_music"
        if any(w in low for w in INTENT_KEYWORDS["get_weather"]): return "get_weather"
        if any(w in low for w in INTENT_KEYWORDS["calculate"]): return "calculate"
        if any(w in low for w in INTENT_KEYWORDS["check_expenses"]): return "check_expenses"
        if any(w in low for w in INTENT_KEYWORDS["get_news"]): return "get_news"
        if any(w in low for w in INTENT_KEYWORDS["get_quote"]): return "get_quote"
        return "unknown"

    def core_select_tool(intent: str) -> str:
        mapping = {
            "show_bookings": "MovieBookingService",
            "play_music": "SpotifyAPI",
            "get_weather": "OpenMeteoWeatherAPI",
            "calculate": "SafeMathCalculator",
            "check_expenses": "ExpenseTrackerService",
            "get_news": "GNewsAPI",
            "get_quote": "MotivationalQuoteGenerator",
        }
        return mapping.get(intent, "DefaultHelpAssistant")

    def execute_tool(intent: str, user_input: str) -> str:
        return f"Executed tool for intent: {intent}"


# ============================================================================
# Task 2: Required Python function detect_intent(user_input)
# ============================================================================

def detect_intent(user_input: str) -> str:
    """
    Takes a user's message as input and returns the detected intent as a string.

    Examples:
    - 'Show me my upcoming movie bookings' -> 'show_bookings'
    - 'Play some jazz music on Spotify'   -> 'play_music'
    - 'What is the weather in Ahmedabad?' -> 'get_weather'
    - 'Calculate 23+7*2'                  -> 'calculate'
    - 'How much did I spend on Food?'     -> 'check_expenses'
    - 'Give me top technology news'       -> 'get_news'
    - 'Inspire me with a quote'           -> 'get_quote'

    Args:
        user_input: Raw string message from user.

    Returns:
        str: Detected intent identifier.
    """
    return core_detect_intent(user_input)


# ============================================================================
# Task 3: Required Python function select_tool(intent)
# ============================================================================

def select_tool(intent: str) -> str:
    """
    Decides which tool or API to use based on the detected intent.

    Examples:
    - 'show_bookings'  -> 'MovieBookingService'
    - 'play_music'     -> 'SpotifyAPI'
    - 'get_weather'    -> 'OpenMeteoWeatherAPI'
    - 'calculate'      -> 'SafeMathCalculator'
    - 'check_expenses' -> 'ExpenseTrackerService'
    - 'get_news'       -> 'GNewsAPI'
    - 'get_quote'      -> 'MotivationalQuoteGenerator'

    Args:
        intent: Detected intent string.

    Returns:
        str: Name of the tool or API to invoke.
    """
    return core_select_tool(intent)


# ============================================================================
# Streamlit Application Configuration
# ============================================================================

st.set_page_config(
    page_title="Personal Assistant Agent (Part 2)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-intent {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
        margin-right: 0.4rem;
    }
    .badge-tool {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }
    .memory-card {
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid #E2E8F0;
        background: #F8FAFC;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Task 4: Memory Feature Initialization (conversation_history)
# ============================================================================

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Expose global reference to conversation_history for programmatic verification
conversation_history: List[Dict[str, Any]] = st.session_state.conversation_history


# ============================================================================
# Sidebar: Agent Status, Memory Monitor & Quick Action Chips
# ============================================================================

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80", use_container_width=True)
    st.markdown("### 🤖 Personal Assistant: **Aria**")
    st.caption("Session 25: Building a Personal Assistant Agent (Part 2)")
    st.markdown("---")

    st.markdown("#### ⚡ Quick Intent Prompts")
    st.caption("Click any sample query to test intent detection and tool routing:")

    quick_prompts = [
        ("🎟️ Movie Bookings", "Show me my upcoming movie bookings"),
        ("🎵 Play Music", "Play some upbeat jazz music on Spotify"),
        ("🌤️ Weather Check", "What is the current weather in Ahmedabad?"),
        ("🧮 Math Calculation", "Calculate 23+7*2"),
        ("💳 Food Expenses", "How much total did I spend on Food?"),
        ("📰 Tech News", "Show me the top 3 technology news headlines"),
        ("💡 Daily Motivation", "Give me a short motivational quote for coding"),
    ]

    selected_prompt = None
    for label, query_text in quick_prompts:
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            selected_prompt = query_text

    st.markdown("---")
    st.markdown("#### 🛠️ Available Tool Registry")
    for intent_name, info in TOOL_REGISTRY.items():
        st.markdown(f"• **{info.get('icon', '🔧')} `{info.get('tool_id')}`**\n  *{info.get('description')}*")

    st.markdown("---")
    if st.button("🗑️ Clear Conversation Memory", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()


# ============================================================================
# Main Content Area: Header & Chat Interface
# ============================================================================

st.markdown('<div class="main-header">🤖 Aria: Personal Assistant Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Tool Orchestrator with Intent Detection, Tool Selection & Active 3-Exchange Memory</div>', unsafe_allow_html=True)

# Layout: Split into Chat Workspace and Memory Monitor
col_chat, col_memory = st.columns([6, 4], gap="large")

with col_chat:
    st.markdown("### 💬 Chat with Assistant")
    st.caption("Type any request below. The agent will detect your intent, select the appropriate tool, and report execution status.")

    # Container for message history
    chat_container = st.container()

    # Display full chat message history in chat bubbles
    with chat_container:
        if not st.session_state.conversation_history:
            st.info("👋 Hello! I am your Personal Assistant Agent. Type a request or click a quick prompt on the sidebar to get started.")
        else:
            for exchange in st.session_state.conversation_history:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(exchange["user"])

                with st.chat_message("assistant", avatar="🤖"):
                    # Badges for Intent & Tool
                    intent_badge = f'<span class="badge-intent">🎯 Intent: {exchange.get("intent", "general")}</span>'
                    tool_badge = f'<span class="badge-tool">🛠️ Tool: {exchange.get("tool", "API")}</span>'
                    st.markdown(f"{intent_badge} {tool_badge}", unsafe_allow_html=True)
                    st.markdown(exchange["agent"])

    # User Input Field (Chat Input or Quick Prompt)
    user_input = st.chat_input("Type your request here (e.g., 'Show me my upcoming movie bookings')...")

    # If quick prompt was clicked, use it as user_input
    if selected_prompt:
        user_input = selected_prompt

    if user_input:
        # Display the user's message immediately
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

        # --------------------------------------------------------------------
        # Task 2: Detect Intent
        # --------------------------------------------------------------------
        detected_intent = detect_intent(user_input)

        # --------------------------------------------------------------------
        # Task 3: Select Tool
        # --------------------------------------------------------------------
        selected_tool = select_tool(detected_intent)

        # --------------------------------------------------------------------
        # Task 5: UI Feedback (Status Message & Loading Spinner)
        # --------------------------------------------------------------------
        feedback_placeholder = st.empty()
        with feedback_placeholder.container():
            st.info(f"🎯 **Intent Detected:** `{detected_intent}` | 🛠️ **Routing to Tool:** `{selected_tool}`")

            with st.spinner(f"⏳ Agent is gathering information and executing task via **{selected_tool}**..."):
                # Simulate realistic gathering/execution time
                time.sleep(0.6)
                # Execute the selected tool
                agent_response = execute_tool(detected_intent, user_input)

        feedback_placeholder.empty()

        # Display the assistant's response
        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                intent_badge = f'<span class="badge-intent">🎯 Intent: {detected_intent}</span>'
                tool_badge = f'<span class="badge-tool">🛠️ Tool: {selected_tool}</span>'
                st.markdown(f"{intent_badge} {tool_badge}", unsafe_allow_html=True)
                st.markdown(agent_response)

        # --------------------------------------------------------------------
        # Task 4: Memory Feature: Save to conversation_history
        # --------------------------------------------------------------------
        exchange_record = {
            "user": user_input,
            "agent": agent_response,
            "intent": detected_intent,
            "tool": selected_tool,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        }
        st.session_state.conversation_history.append(exchange_record)
        st.rerun()


# ============================================================================
# Task 4: UI Display of Last Three Exchanges in conversation_history
# ============================================================================

with col_memory:
    st.markdown("### 🧠 Agent Memory Monitor")
    st.markdown("**Constraint:** Display the last three exchanges from `conversation_history`.")
    st.caption(f"Total History Entries: {len(st.session_state.conversation_history)}")

    # Slice the last three exchanges
    recent_exchanges = st.session_state.conversation_history[-3:]

    if not recent_exchanges:
        st.warning("⚠️ Memory is currently empty. Send a message to populate `conversation_history`.")
    else:
        st.success(f"Displaying **{len(recent_exchanges)}** most recent exchange(s) from memory window:")

        for i, exchange in enumerate(reversed(recent_exchanges), start=1):
            with st.expander(f"Exchange #{len(st.session_state.conversation_history) - i + 1} — [{exchange.get('timestamp')}] Intent: {exchange.get('intent')}", expanded=(i == 1)):
                st.markdown(f"**👤 User Request:**\n> {exchange['user']}")
                st.markdown(f"**🎯 Detected Intent:** `{exchange.get('intent')}`")
                st.markdown(f"**🛠️ Selected Tool:** `{exchange.get('tool')}`")
                st.markdown(f"**🤖 Agent Response:**\n{exchange['agent']}")

    # Raw Memory JSON Viewer for Telemetry
    with st.expander("🔍 Inspect Raw `conversation_history[-3:]` Data", expanded=False):
        st.json(recent_exchanges)
