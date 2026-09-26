# ============================================
# Task 3: Spotify Agent with Memory
# File: spotify_agent.py
# ============================================

from langchain.memory import ConversationBufferMemory

# Memory stores conversation history
memory = ConversationBufferMemory(return_messages=True)

last_queries = []

def spotify_agent(user_input):
    global last_queries

    # Save user query
    memory.save_context(
        {"input": user_input},
        {"output": "Processed"}
    )

    # Keep only last 2 queries
    last_queries.append(user_input)
    last_queries = last_queries[-2:]

    # User asks previous queries
    if user_input.lower() == "what did i ask before?":
        if last_queries[:-1]:
            return "Your last queries were: " + ", ".join(last_queries[:-1])
        else:
            return "You have not asked anything before."

    # Normal responses
    if "trending" in user_input.lower():
        return "Fetching trending songs from Spotify."

    elif "playlist" in user_input.lower():
        return "Opening your Spotify playlist."

    else:
        return "Spotify request received."


print("====== Spotify AI Agent with Memory ======")
print("Type 'exit' to stop.\n")

while True:

    query = input("You: ")

    if query.lower() == "exit":
        print("Agent: Goodbye!")
        break

    answer = spotify_agent(query)

    print("Agent:", answer)