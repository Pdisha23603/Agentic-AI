# ============================================
# Task 3: ReAct Pattern (Reason + Action)
# ============================================

def cricket_assistant(question):
    print("=== Virtual Cricket Assistant ===")

    # Reason Step (High-level planning)
    print("[Reason] Understanding the cricket-related question.")

    if "last ipl match" in question.lower():
        print("[Reason] The user is asking for the latest IPL match result.")

        # Action Step
        print("[Action] Fetching latest IPL match information...")
        print("Answer: Royal Challengers Bengaluru won the last IPL match.")

    else:
        print("[Action] Sorry, I can answer only IPL-related questions.")


# Example
cricket_assistant("Who won the last IPL match?")