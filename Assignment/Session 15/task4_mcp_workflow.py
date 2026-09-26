# ---------------------------------------------
# TASK 4 : BookMyShow Review Workflow
# LangChain + LangGraph
# ---------------------------------------------

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

review = """
The movie has stunning visuals and excellent background music.
The first half is engaging, but the second half feels slow.
Overall it is worth watching in IMAX with friends.
"""

# ------------------------
# State
# ------------------------

class MovieState(TypedDict):
    summary: str
    choice: str

# ------------------------
# Node 1
# ------------------------

def summarize_review(state: MovieState):

    prompt = f"""
Summarize this movie review in 2 lines.

Review:
{review}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    state["summary"] = response.content

    print("\nMovie Review Summary")
    print(state["summary"])

    return state

# ------------------------
# Node 2
# ------------------------

def ask_user(state: MovieState):

    state["choice"] = input(
        "\nDo you want more movie details? (yes/no): "
    )

    return state

# ------------------------
# Node 3
# ------------------------

def follow_up(state: MovieState):

    if state["choice"].lower() == "yes":

        print("\nMovie Details")
        print("Genre : Action / Adventure")
        print("Duration : 2 Hours 45 Minutes")
        print("Rating : 4.5 / 5")
        print("Best Experience : IMAX")

    else:

        print("\nEnjoy your movie!")

    return state

# ------------------------
# Graph
# ------------------------

graph = StateGraph(MovieState)

graph.add_node("SummarizeReview", summarize_review)
graph.add_node("AskUser", ask_user)
graph.add_node("FollowUp", follow_up)

graph.add_edge(START, "SummarizeReview")
graph.add_edge("SummarizeReview", "AskUser")
graph.add_edge("AskUser", "FollowUp")
graph.add_edge("FollowUp", END)

app = graph.compile()

app.invoke({
    "summary": "",
    "choice": ""
})