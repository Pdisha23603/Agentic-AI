"""
Session 15 - Task 4: BookMyShow Review Pipeline (LangChain + LangGraph MCP)
==========================================================================
This script demonstrates a Multi-Component Pipeline (MCP) workflow chaining:
1. LangChain: Summarizes a detailed BookMyShow movie review using LCEL.
2. LangGraph: Manages the stateful user interaction flow, asking if the user
   wants more details and branching to provide cast/showtime details or a farewell.
"""

import sys
import os
import re
from typing import TypedDict, Optional, Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.graph import StateGraph, START, END

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Sample BookMyShow Critic Review for "Kalki 2898 AD"
BMS_MOVIE_REVIEW = """
BookMyShow Verified Critic Review - 'Kalki 2898 AD' (Sci-Fi / Mythological Epic)
Rating: 4.5 / 5 Stars | Certified Fresh
Reviewer: BookMyShow Editorial Cinema Desk

Nag Ashwin's ambitious sci-fi epic 'Kalki 2898 AD' marries Indian Mahabharata lore with
a dystopian cyberpunk future inspired by Mad Max and Blade Runner. Set in the desolate year
2898 AD in the world's last city of Kasi, the film follows Supreme Yaskin (Kamal Haasan)
who controls the totalitarian Complex.

Amitabh Bachchan as the immortal warrior Ashwatthama delivers a career-defining performance
brimming with raw mythological gravitas and fierce battle sequences. Prabhas plays the carefree
bounty hunter Bhairava with charisma and comedic flair before stepping into heroics.
Deepika Padukone shines with quiet dignity as SUM-80, the carrier of the miraculous divine child.

The world-building is staggering for Indian cinema: Bujji (the AI vehicle voiced by Keerthy Suresh)
adds high-tech fun, and Santhosh Narayanan's thumping background score elevates every clash.
While the first half spends time setting up the extensive lore and has occasional pacing dips,
the breathtaking final 40 minutes deliver an exhilarating cinematic spectacle that leaves
the audience spellbound.
"""

MOVIE_DETAILS = {
    "title": "Kalki 2898 AD",
    "director": "Nag Ashwin",
    "producers": "Vyjayanthi Movies (C. Aswani Dutt)",
    "cast": [
        "Amitabh Bachchan as Ashwatthama",
        "Prabhas as Bhairava",
        "Deepika Padukone as SUM-80",
        "Kamal Haasan as Supreme Yaskin",
        "Disha Patani as Roxie",
        "Keerthy Suresh (Voice of Bujji)"
    ],
    "music": "Santhosh Narayanan",
    "box_office": "Rs. 1,200+ Crores Worldwide",
    "recommended_format": "IMAX 3D / 4DX for supreme visual effects experience"
}

# ==============================================================================
# COMPONENT 1: LangChain Review Summarizer
# ==============================================================================
SUMMARIZE_PROMPT = """You are a BookMyShow Film Critic.
Summarize the following movie review in 3 concise bullet points:
- Verdict & Rating
- Key Cinematic Highlights & Performances
- Minor Flaws / Pacing

REVIEW:
{review}

CONCISE SUMMARY:"""

def build_langchain_summarizer():
    prompt = PromptTemplate(input_variables=["review"], template=SUMMARIZE_PROMPT)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        except Exception:
            llm = _create_mock_summary_llm()
    else:
        llm = _create_mock_summary_llm()

    return prompt | llm | StrOutputParser()

def _create_mock_summary_llm():
    summary_text = (
        "• VERDICT: 4.5/5 Stars - A visually staggering, ambitious fusion of Hindu mythology and dystopian cyberpunk.\n"
        "• HIGHLIGHTS: Amitabh Bachchan's monumental performance as Ashwatthama, Prabhas's charismatic bounty hunter Bhairava, and an exhilarating climax.\n"
        "• PACING NOTE: Initial world-building is slightly slow in the first half, but pays off massively in the last 40 minutes."
    )
    return FakeListChatModel(responses=[summary_text])

# ==============================================================================
# COMPONENT 2: LangGraph User Interaction Flow
# ==============================================================================
class BMSPipelineWorkflowState(TypedDict):
    movie_title: str
    review_text: str
    summary: str
    user_response: Optional[str]
    agent_message: str
    next_step: str

def summarize_step_node(state: BMSPipelineWorkflowState) -> Dict:
    """Step 1 (LangChain): Summarize BookMyShow review and prompt user."""
    summarizer = build_langchain_summarizer()
    summary = summarizer.invoke({"review": state["review_text"]})

    prompt_msg = (
        f"[BookMyShow Review Summary: {state['movie_title']}]\n"
        f"{'-' * 60}\n"
        f"{summary}\n"
        f"{'-' * 60}\n"
        f"Would you like more details about the cast, director, and trivia? (yes/no)"
    )
    return {
        "summary": summary,
        "agent_message": prompt_msg,
        "next_step": "await_user"
    }

def route_user_decision(state: BMSPipelineWorkflowState) -> str:
    """Evaluates user response using robust whole-word token matching."""
    resp = (state.get("user_response") or "").lower().strip()
    words = set(re.findall(r'\b[a-z]+\b', resp))

    # Explicit negative check
    if any(neg in words for neg in ["no", "nope", "nah", "never", "not"]):
        return "farewell"

    # Explicit positive check
    positive_words = {"yes", "y", "sure", "yeah", "yep", "yup", "ok", "okay", "please", "details"}
    if words.intersection(positive_words) or "tell me" in resp:
        return "provide_details"

    return "farewell"

def provide_details_node(state: BMSPipelineWorkflowState) -> Dict:
    """Step 2A: Displays comprehensive movie details upon user confirmation."""
    cast_list = "\n".join([f"     * {actor}" for actor in MOVIE_DETAILS["cast"]])
    details_msg = (
        f"Full Movie Details for '{MOVIE_DETAILS['title']}':\n"
        f"   • Director:           {MOVIE_DETAILS['director']}\n"
        f"   • Production House:   {MOVIE_DETAILS['producers']}\n"
        f"   • Music Director:     {MOVIE_DETAILS['music']}\n"
        f"   • Box Office Gross:   {MOVIE_DETAILS['box_office']}\n"
        f"   • Recommended Screen: {MOVIE_DETAILS['recommended_format']}\n"
        f"   • Star Cast:\n{cast_list}\n\n"
        f"Ready to book tickets? Check available showtimes on BookMyShow!"
    )
    return {"agent_message": details_msg, "next_step": "completed"}

def farewell_node(state: BMSPipelineWorkflowState) -> Dict:
    """Step 2B: Courteous farewell message."""
    farewell_msg = (
        "No problem! Enjoy your movie viewing, and reach out anytime you need "
        "ratings, reviews, or showtimes on BookMyShow!"
    )
    return {"agent_message": farewell_msg, "next_step": "completed"}

def build_mcp_pipeline_graph():
    builder = StateGraph(BMSPipelineWorkflowState)

    builder.add_node("summarize_review", summarize_step_node)
    builder.add_node("provide_details", provide_details_node)
    builder.add_node("farewell", farewell_node)

    builder.add_edge(START, "summarize_review")
    builder.add_conditional_edges(
        "summarize_review",
        route_user_decision,
        {
            "provide_details": "provide_details",
            "farewell": "farewell"
        }
    )
    builder.add_edge("provide_details", END)
    builder.add_edge("farewell", END)

    return builder.compile()

def run_task4():
    print("=" * 70)
    print("  SESSION 15 - TASK 4: BOOKMYSHOW PIPELINE (LANGCHAIN + LANGGRAPH)")
    print("=" * 70)

    graph = build_mcp_pipeline_graph()

    # Branch 1: User says YES to more details
    print("\n--- TEST BRANCH A: User confirms ('Yes, show details') ---")
    state_a = {
        "movie_title": "Kalki 2898 AD",
        "review_text": BMS_MOVIE_REVIEW,
        "summary": "",
        "user_response": "Yes, please share more details about cast and trivia!",
        "agent_message": "",
        "next_step": ""
    }
    result_a = graph.invoke(state_a)
    print("\n[LangChain Summary Output]:")
    print(result_a["summary"])
    print("\n[LangGraph Follow-up Response (Details Branch)]:")
    print(result_a["agent_message"])

    # Branch 2: User says NO to more details
    print("\n" + "=" * 70)
    print("--- TEST BRANCH B: User declines ('No thanks') ---")
    state_b = {
        "movie_title": "Kalki 2898 AD",
        "review_text": BMS_MOVIE_REVIEW,
        "summary": "",
        "user_response": "No thanks, that summary was enough.",
        "agent_message": "",
        "next_step": ""
    }
    result_b = graph.invoke(state_b)
    print("\n[LangGraph Follow-up Response (Farewell Branch)]:")
    print(result_b["agent_message"])

    print("\n" + "=" * 70)
    print("[SUCCESS] Task 4 completed: LangChain summarization chained with LangGraph flow!")

if __name__ == "__main__":
    if "--interactive" in sys.argv:
        summarizer = build_langchain_summarizer()
        summary = summarizer.invoke({"review": BMS_MOVIE_REVIEW})
        print(f"\nSummary of 'Kalki 2898 AD':\n{summary}")
        ans = input("\nWould you like more details about cast, director, and trivia? (yes/no): ").strip()
        graph = build_mcp_pipeline_graph()
        res = graph.invoke({
            "movie_title": "Kalki 2898 AD",
            "review_text": BMS_MOVIE_REVIEW,
            "summary": summary,
            "user_response": ans,
            "agent_message": "",
            "next_step": ""
        })
        print(f"\n{res['agent_message']}")
    else:
        run_task4()
