"""
Session 15 - Task 5: Twitter Trends Summarizer with LangChain
=============================================================
This script fetches and summarizes trending topics from a Mock Twitter API
using LangChain, and prints the top 2 trends in the console.

Original AI-generated snippet (ChatGPT / Copilot) included in docstring below,
along with production refactoring to modern LangChain Expression Language (LCEL).

--------------------------------------------------------------------------------
ORIGINAL AI-GENERATED CODE SNIPPET (ChatGPT / Copilot):
--------------------------------------------------------------------------------
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests

def get_twitter_trends():
    response = requests.get("https://api.mock-twitter.com/v2/trends")
    return response.json()

prompt = PromptTemplate(
    input_variables=["topic", "tweets"],
    template="Summarize the following Twitter trending topic {topic} based on these tweets:\n{tweets}"
)

llm = OpenAI(temperature=0.7)
chain = LLMChain(llm=llm, prompt=prompt)

trends = get_twitter_trends()
for trend in trends:
    summary = chain.run(topic=trend['name'], tweets=trend['sample_tweets'])
    print(f"Trend: {trend['name']}")
    print(f"Summary: {summary}")
--------------------------------------------------------------------------------
"""

import sys
import os
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# 1. Mock Twitter API (Simulating Twitter / X API v2 GET /2/trends/by/woeid)
# ==============================================================================
class MockTwitterAPI:
    """Simulates real-world Twitter v2 Trends Endpoint without broken network URLs."""

    @staticmethod
    def get_india_trends() -> List[Dict]:
        return [
            {
                "name": "#Gaganyaan",
                "category": "Science & Space Technology",
                "tweet_volume": 342500,
                "sample_tweets": [
                    "ISRO successfully completes the critical Crew Escape System test for Gaganyaan!",
                    "Proud moment for India as astronaut test pilots finish rigorous centrifuge training.",
                    "PM congratulates ISRO scientists on human spaceflight mission milestone.",
                    "Live visuals of the orbital capsule splashdown recovery in Bay of Bengal."
                ]
            },
            {
                "name": "#IPLRetentions",
                "category": "Sports / Cricket",
                "tweet_volume": 287100,
                "sample_tweets": [
                    "BCCI confirms IPL 2025 retention rules: Teams allowed up to 6 retentions including RTM.",
                    "Huge speculation whether MS Dhoni will be retained under the uncapped player rule for CSK.",
                    "Mumbai Indians lock in Jasprit Bumrah and Hardik Pandya as top tier retentions.",
                    "Rishabh Pant and KL Rahul retention talks ignite mega auction excitement."
                ]
            },
            {
                "name": "#AIAdvancements",
                "category": "Technology & AI",
                "tweet_volume": 194300,
                "sample_tweets": [
                    "New multimodal models achieve near human parity in complex reasoning benchmarks.",
                    "Open-source local LLMs running effortlessly on consumer hardware."
                ]
            },
            {
                "name": "#MonsoonAlert",
                "category": "Weather",
                "tweet_volume": 85000,
                "sample_tweets": [
                    "IMD issues orange alert for heavy rainfall across coastal regions."
                ]
            }
        ]

# ==============================================================================
# 2. Refactored LangChain LCEL Summarization Pipeline
# ==============================================================================
TREND_SUMMARY_PROMPT = """You are a Social Media Intelligence Analyst.
Analyze and summarize why the topic '{topic}' is trending on Twitter/X based on these viral tweets:

TWEETS:
{tweets}

Provide a concise 2-sentence summary explaining:
1. What major event or news triggered this trend.
2. The prevailing public reaction on social media.

EXCISE SUMMARY:"""

def build_trend_summarizer():
    prompt = PromptTemplate(
        input_variables=["topic", "tweets"],
        template=TREND_SUMMARY_PROMPT
    )

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        except Exception:
            llm = _create_mock_trend_llm()
    else:
        llm = _create_mock_trend_llm()

    # Modern LCEL: Prompt | LLM | StrOutputParser
    return prompt | llm | StrOutputParser()

def _create_mock_trend_llm():
    responses = [
        # Summary for Trend 1: #Gaganyaan
        "ISRO achieved a major breakthrough by successfully completing the Crew Escape System test and capsule splashdown recovery for the Gaganyaan mission. The public and national leaders are celebrating this milestone with immense national pride.",
        # Summary for Trend 2: #IPLRetentions
        "The BCCI officially announced the IPL 2025 retention regulations allowing up to six players per franchise via direct retention and RTM cards. Fans and cricket commentators are intensely debating team strategies, especially regarding MS Dhoni and key franchise superstars."
    ]
    return FakeListChatModel(responses=responses)

# ==============================================================================
# 3. Execution & Printing Top 2 Trends
# ==============================================================================
def run_task5():
    print("=" * 70)
    print("      SESSION 15 - TASK 5: TWITTER TRENDS SUMMARIZER (LANGCHAIN)")
    print("=" * 70)

    print("\n[+] FETCHING TRENDS FROM MOCK TWITTER API...")
    all_trends = MockTwitterAPI.get_india_trends()

    # Sort by tweet volume descending and slice strictly to TOP 2
    sorted_trends = sorted(all_trends, key=lambda x: x["tweet_volume"], reverse=True)
    top_2_trends = sorted_trends[:2]

    print(f"[*] Total trends fetched: {len(all_trends)}")
    print(f"[*] Filtering strictly to TOP 2 trends as requested:\n")

    summarizer = build_trend_summarizer()

    for rank, trend in enumerate(top_2_trends, start=1):
        formatted_tweets = "\n".join([f"  - \"{t}\"" for t in trend["sample_tweets"]])
        
        # Invoke modern LangChain LCEL pipeline
        summary = summarizer.invoke({
            "topic": trend["name"],
            "tweets": formatted_tweets
        })

        print("=" * 70)
        print(f"TOP #{rank} TREND: {trend['name']}  ({trend['tweet_volume']:,} Tweets)")
        print(f"Category:     {trend['category']}")
        print("-" * 70)
        print("Sample Viral Tweets:")
        print(formatted_tweets)
        print("-" * 70)
        print(f"LangChain AI Summary:")
        print(f"  >>> {summary.strip()}")
        print("=" * 70 + "\n")

    print("[SUCCESS] Task 5 completed: Top 2 Twitter trends fetched and summarized!")

if __name__ == "__main__":
    run_task5()
