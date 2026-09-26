# ---------------------------------------------
# TASK 5 : Mock Twitter Trends Summarizer
# ---------------------------------------------

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# --------------------------
# Mock Twitter API
# --------------------------

mock_twitter_api = {
    "trends": [
        {
            "title": "IPL 2026 Final",
            "tweets": 120000
        },
        {
            "title": "OpenAI GPT-5.6",
            "tweets": 98000
        },
        {
            "title": "ISRO Moon Mission",
            "tweets": 87000
        },
        {
            "title": "India Tech Summit",
            "tweets": 64000
        }
    ]
}

# --------------------------
# Sort Top Trends
# --------------------------

sorted_trends = sorted(
    mock_twitter_api["trends"],
    key=lambda x: x["tweets"],
    reverse=True
)

top2 = sorted_trends[:2]

prompt = f"""
Summarize these Twitter trends in two short bullet points.

{top2}
"""

summary = llm.invoke([HumanMessage(content=prompt)])

print("="*60)
print("TOP 2 TRENDING TOPICS")
print("="*60)

for trend in top2:
    print(f"{trend['title']} ({trend['tweets']} tweets)")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

print(summary.content)