# ============================================
# Task 1: Print Available LangChain Agent Classes
# File: agent_intro.py
# ============================================

import langchain.agents as agents

print("Available Agent Classes in LangChain")
print("-" * 40)

# Print all public classes/functions in langchain.agents
for item in dir(agents):
    if not item.startswith("_"):
        print(item)