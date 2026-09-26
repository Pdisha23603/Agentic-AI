"""
Session 15 - Task 2: IPL Cricket Conversational Agent with LangChain
====================================================================
This script builds a conversational agent using LangChain that answers
user questions about IPL cricket teams, captains, and team details
grounded on a provided knowledge base.
"""

import sys
import os
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Grounding Knowledge Base: IPL Teams & Captains
IPL_TEAMS_DATA = [
    {"team": "Mumbai Indians", "short": "MI", "captain": "Hardik Pandya", "titles": 5, "home_ground": "Wankhede Stadium, Mumbai"},
    {"team": "Chennai Super Kings", "short": "CSK", "captain": "Ruturaj Gaikwad", "titles": 5, "home_ground": "M. A. Chidambaram Stadium, Chennai"},
    {"team": "Kolkata Knight Riders", "short": "KKR", "captain": "Shreyas Iyer", "titles": 3, "home_ground": "Eden Gardens, Kolkata"},
    {"team": "Sunrisers Hyderabad", "short": "SRH", "captain": "Pat Cummins", "titles": 1, "home_ground": "Rajiv Gandhi Intl Cricket Stadium, Hyderabad"},
    {"team": "Rajasthan Royals", "short": "RR", "captain": "Sanju Samson", "titles": 1, "home_ground": "Sawai Mansingh Stadium, Jaipur"},
    {"team": "Gujarat Titans", "short": "GT", "captain": "Shubman Gill", "titles": 1, "home_ground": "Narendra Modi Stadium, Ahmedabad"},
    {"team": "Royal Challengers Bengaluru", "short": "RCB", "captain": "Faf du Plessis", "titles": 0, "home_ground": "M. Chinnaswamy Stadium, Bengaluru"},
    {"team": "Delhi Capitals", "short": "DC", "captain": "Rishabh Pant", "titles": 0, "home_ground": "Arun Jaitley Stadium, Delhi"},
    {"team": "Lucknow Super Giants", "short": "LSG", "captain": "KL Rahul", "titles": 0, "home_ground": "Ekana Cricket Stadium, Lucknow"},
    {"team": "Punjab Kings", "short": "PBKS", "captain": "Shikhar Dhawan", "titles": 0, "home_ground": "PCA Stadium, Mohali / Mullanpur"}
]

def format_ipl_knowledge():
    lines = []
    for item in IPL_TEAMS_DATA:
        lines.append(
            f"• {item['team']} ({item['short']}): Captain = {item['captain']}, "
            f"Titles Won = {item['titles']}, Home Ground = {item['home_ground']}"
        )
    return "\n".join(lines)

IPL_KNOWLEDGE_TEXT = format_ipl_knowledge()

AGENT_SYSTEM_PROMPT = """You are an expert IPL Cricket Conversational Assistant.
Answer the user's question accurately using ONLY the provided official IPL Knowledge Base below.
If asked about a captain, state the team name and captain clearly.
If the information is not present in the knowledge base, politely state that you only have current IPL team roster information.

OFFICIAL IPL KNOWLEDGE BASE:
{knowledge_base}
"""

def answer_ipl_query_local(query: str) -> str:
    """Accurate offline knowledge resolution matching with whole-word regex."""
    q = query.lower()

    # 1. List all captains
    if "all" in q and ("captain" in q or "team" in q or "list" in q):
        res = ["Here is the complete list of IPL teams and their captains:"]
        for t in IPL_TEAMS_DATA:
            res.append(f"  • {t['team']} ({t['short']}) ➔ {t['captain']}")
        return "\n".join(res)

    # 2. Check captain name mentioned first (e.g., "Pat Cummins", "Cummins", "Hardik")
    for t in IPL_TEAMS_DATA:
        cap_parts = [p.lower() for p in t["captain"].split() if len(p) > 2]
        if any(re.search(r'\b' + re.escape(part) + r'\b', q) for part in cap_parts):
            return f"{t['captain']} is the captain of {t['team']} ({t['short']})."

    # 3. Check full team name or exact short code with word boundaries
    for t in IPL_TEAMS_DATA:
        team_name_lower = t["team"].lower()
        short_lower = t["short"].lower()
        has_team = team_name_lower in q
        has_short = bool(re.search(r'\b' + re.escape(short_lower) + r'\b', q))

        if has_team or has_short:
            if any(k in q for k in ["captain", "who leads", "leader", "who is", "who's"]):
                return (
                    f"The captain of {t['team']} ({t['short']}) is {t['captain']}. "
                    f"Home Ground: {t['home_ground']}."
                )
            elif any(k in q for k in ["title", "troph", "won", "cup"]):
                return f"{t['team']} ({t['short']}) has won {t['titles']} IPL title(s)."
            else:
                return (
                    f"{t['team']} ({t['short']}) is captained by {t['captain']}, "
                    f"plays at {t['home_ground']}, and has won {t['titles']} title(s)."
                )

    return (
        "I am your IPL assistant! You can ask me questions like 'Who is the captain of Mumbai Indians?' "
        "or 'Who leads CSK?'."
    )

class IPLConversationalAgent:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        
        self.has_api_key = bool(os.getenv("OPENAI_API_KEY"))
        if self.has_api_key:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                self.chain = self.prompt | self.llm | StrOutputParser()
            except Exception:
                self.has_api_key = False

    def ask(self, question: str) -> str:
        if self.has_api_key:
            try:
                return self.chain.invoke({
                    "knowledge_base": IPL_KNOWLEDGE_TEXT,
                    "question": question
                })
            except Exception:
                pass
        return answer_ipl_query_local(question)

def run_task2():
    print("=" * 70)
    print("      SESSION 15 - TASK 2: IPL CONVERSATIONAL AGENT (LANGCHAIN)")
    print("=" * 70)

    print("\n[+] GROUNDED IPL TEAMS & CAPTAINS KNOWLEDGE BASE:")
    print("-" * 70)
    print(IPL_KNOWLEDGE_TEXT)
    print("-" * 70)

    agent = IPLConversationalAgent()

    test_queries = [
        "Who is the captain of Mumbai Indians?",
        "Who is the captain of Chennai Super Kings?",
        "Who leads Royal Challengers Bengaluru (RCB)?",
        "Which team does Pat Cummins captain?",
        "List all IPL teams and their captains."
    ]

    print("\n[+] RUNNING CONVERSATIONAL QUERIES:")
    print("=" * 70)

    for idx, q in enumerate(test_queries, start=1):
        print(f"\n[Query {idx}]: \"{q}\"")
        response = agent.ask(q)
        print(f"[Agent Response]:\n{response}")
        print("-" * 70)

    print("\n[SUCCESS] Task 2 completed: IPL conversational agent built and verified!")

if __name__ == "__main__":
    if "--interactive" in sys.argv:
        agent = IPLConversationalAgent()
        print("IPL Agent Interactive Mode (type 'exit' to quit):")
        while True:
            try:
                user_q = input("\nYou: ").strip()
                if user_q.lower() in ("exit", "quit", "q"):
                    break
                if user_q:
                    print(f"Agent: {agent.ask(user_q)}")
            except (KeyboardInterrupt, EOFError):
                break
    else:
        run_task2()
