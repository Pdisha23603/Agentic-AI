"""
Session 24 - Task 3: GNews API Technology Headlines Integration
----------------------------------------------------------------
Integrates the GNews API (https://gnews.io/) to fetch and display the top 3
latest technology news headlines.

Features:
- Configurable API key via environment variable 'GNEWS_API_KEY' or CLI argument
- Queries 'https://gnews.io/api/v4/top-headlines?category=technology&lang=en&max=3'
- Graceful offline / demo fallback mode with realistic tech headlines
- Formatted output with Headline title, description, source, publication date, and URL
"""

import sys
import os
import requests
from typing import Dict, List, Any, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Fallback realistic technology news headlines for offline/unauthenticated execution
FALLBACK_TECH_HEADLINES = [
    {
        "title": "Autonomous AI Agents Reshape Enterprise Workflow Automation and Multi-Tool Systems",
        "description": "Next-generation agentic frameworks allow autonomous LLM agents to plan, execute multi-step APIs, and coordinate with zero human intervention.",
        "url": "https://techcrunch.com/2026/09/autonomous-ai-agents-enterprise",
        "publishedAt": "2026-09-26T08:30:00Z",
        "source": {"name": "TechCrunch", "url": "https://techcrunch.com"},
    },
    {
        "title": "Breakthrough in Photonic Quantum Computing Achieves Room-Temperature Coherence",
        "description": "Researchers demonstrate scalable silicon photonic chips operating at ambient temperatures, reducing cooling overhead for quantum data centers.",
        "url": "https://wired.com/2026/09/photonic-quantum-coherence",
        "publishedAt": "2026-09-26T07:15:00Z",
        "source": {"name": "Wired", "url": "https://wired.com"},
    },
    {
        "title": "Open-Source Reasoning Models Set New Benchmarks in Code Synthesis and Mathematical Logic",
        "description": "The open-source AI community releases advanced distilled reasoning architectures that compete directly with frontier proprietary models on complex code generation.",
        "url": "https://arstechnica.com/2026/09/open-source-reasoning-models",
        "publishedAt": "2026-09-26T06:00:00Z",
        "source": {"name": "Ars Technica", "url": "https://arstechnica.com"},
    },
]


def fetch_tech_headlines(
    api_key: Optional[str] = None,
    max_results: int = 3,
    category: str = "technology",
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Fetches top technology news headlines from GNews API.

    Args:
        api_key: GNews API key (if None, reads from GNEWS_API_KEY environment variable).
        max_results: Number of headlines to retrieve (default: 3).
        category: News category (default: 'technology').
        timeout: Request timeout in seconds.

    Returns:
        Dict containing success status, source_mode ('live' or 'demo_fallback'),
        and list of article dictionaries.
    """
    resolved_key = api_key or os.getenv("GNEWS_API_KEY")

    # If no API key provided, fall back gracefully
    if not resolved_key or resolved_key.strip() in ("", "YOUR_GNEWS_API_KEY", "dummy_key"):
        return {
            "success": True,
            "source_mode": "demo_fallback",
            "message": (
                "ℹ️  [Notice] No valid 'GNEWS_API_KEY' found in environment or arguments.\n"
                "    To use live GNews API data:\n"
                "    1. Sign up for a free key at https://gnews.io/\n"
                "    2. Set it via: set GNEWS_API_KEY=\"your_api_key_here\" (Windows)\n"
                "       or pass it via: python task3_gnews_headlines.py <your_api_key>\n"
                "    Demonstrating with high-fidelity technology news headlines:"
            ),
            "articles": FALLBACK_TECH_HEADLINES[:max_results],
        }

    # Live API Call
    endpoint = "https://gnews.io/api/v4/top-headlines"
    params = {
        "category": category,
        "lang": "en",
        "max": max_results,
        "apikey": resolved_key.strip(),
    }

    try:
        response = requests.get(endpoint, params=params, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            return {
                "success": True,
                "source_mode": "live",
                "message": f"✅ Successfully fetched {len(articles)} live headlines from GNews API.",
                "articles": articles[:max_results],
            }
        else:
            # Handle API errors (e.g., 401 Unauthorized, 403, 429 Quota Exceeded)
            err_msg = f"HTTP {response.status_code}: {response.text}"
            return {
                "success": True,  # Return fallback so caller doesn't crash
                "source_mode": "fallback_on_api_error",
                "message": f"⚠️  GNews API returned error ({err_msg}). Reverting to fallback headlines.",
                "articles": FALLBACK_TECH_HEADLINES[:max_results],
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": True,
            "source_mode": "fallback_on_network_error",
            "message": f"⚠️  Network connection to GNews failed ({str(e)}). Reverting to fallback headlines.",
            "articles": FALLBACK_TECH_HEADLINES[:max_results],
        }


def display_tech_headlines(headline_data: Dict[str, Any]) -> None:
    """Displays the top 3 headlines in a structured, readable format."""
    print("=" * 70)
    print(" 📰  TOP 3 LATEST TECHNOLOGY NEWS HEADLINES (GNEWS API)")
    print("=" * 70)

    if headline_data.get("message"):
        print(headline_data["message"])
        print("-" * 70)

    articles = headline_data.get("articles", [])
    if not articles:
        print("❌ No news articles found.")
        print("=" * 70)
        return

    for idx, article in enumerate(articles, start=1):
        title = article.get("title", "No Title")
        desc = article.get("description", "No description available.")
        url = article.get("url", "N/A")
        pub_at = article.get("publishedAt", "N/A")
        source_obj = article.get("source", {})
        source_name = source_obj.get("name") if isinstance(source_obj, dict) else str(source_obj)
        source_name = source_name or "Unknown Source"

        print(f"\n[{idx}] 📌 {title}")
        print(f"    🏢 Publisher : {source_name}")
        print(f"    🕒 Published : {pub_at}")
        print(f"    📝 Summary   : {desc}")
        print(f"    🔗 Read More : {url}")
        print("-" * 70)

    print("=" * 70)


def main():
    """Main execution entry point."""
    api_key_arg = sys.argv[1] if len(sys.argv) > 1 else None
    headline_result = fetch_tech_headlines(api_key=api_key_arg, max_results=3)
    display_tech_headlines(headline_result)


if __name__ == "__main__":
    main()
