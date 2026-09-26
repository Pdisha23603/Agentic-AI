# SESSION 15 – LangChain + LangGraph + MCP Integration

This repository contains the complete implementation and solutions for all tasks under **Session 15: LangChain + LangGraph + MCP Integration**.

---

## Overview of Tasks & Files Created

| Task | Topic | Files Created | Description |
| :--- | :--- | :--- | :--- |
| **Task 1** | Flipkart Product Review Summarizer | [`task1_flipkart_review_summarizer.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task1_flipkart_review_summarizer.py) | LangChain LCEL pipeline summarizing an authentic Flipkart product review (pros, cons, sentiment, verdict). |
| **Task 2** | IPL Cricket Conversational Agent | [`task2_ipl_conversational_agent.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task2_ipl_conversational_agent.py) | LangChain conversational Q&A agent grounded on official IPL team rosters and captains. |
| **Task 3** | Zomato Recommender Flow | [`task3_zomato_langgraph.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task3_zomato_langgraph.py) | LangGraph `StateGraph` conditional workflow: detects city -> prompts if missing -> returns 3 top restaurants. |
| **Task 4** | BookMyShow Review Pipeline (MCP) | [`task4_bms_langchain_langgraph_mcp.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task4_bms_langchain_langgraph_mcp.py) | Multi-Component Pipeline: LangChain review summarizer + LangGraph user interaction branching state machine. |
| **Task 5** | Twitter Trends Summarizer | [`task5_twitter_trends_langchain.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task5_twitter_trends_langchain.py)<br>[`task5_ai_code_evolution.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task5_ai_code_evolution.md) | Upgraded ChatGPT/Copilot code snippet into modern LangChain LCEL, fetching & summarizing top 2 Twitter trends. |

---

## Detailed Task Documentation & Execution

### Task 1: Flipkart Review Summarizer with LangChain
- **Goal**: Summarize a Flipkart product review using LangChain LCEL (`PromptTemplate | LLM | StrOutputParser`), displaying both original review and summary.
- **To Run**:
  ```bash
  python task1_flipkart_review_summarizer.py
  ```
- **Console Output Preview**:
  - Displays original Nothing Phone (2a) review.
  - Generates structured summary: Sentiment (4.5/5), Key Positives (AMOLED display, Glyph interface, battery life), Key Negatives (no charger in box), Final Recommendation.

---

### Task 2: IPL Cricket Conversational Agent
- **Goal**: Build a conversational agent answering questions about IPL teams and captains (e.g. *"Who is the captain of Mumbai Indians?"*).
- **Features**:
  - Grounded on all 10 IPL franchises (MI, CSK, KKR, SRH, RR, GT, RCB, DC, LSG, PBKS).
  - Handles variations like captain names, team short codes, home venues, and title counts.
  - Interactive mode available via `--interactive`.
- **To Run**:
  ```bash
  # Automated test queries:
  python task2_ipl_conversational_agent.py

  # Interactive chat:
  python task2_ipl_conversational_agent.py --interactive
  ```

---

### Task 3: Zomato Restaurant Recommender with LangGraph
- **Goal**: Design a conversational flow where the agent checks for the user's city, asks for the city if missing, and suggests 3 restaurants from a hardcoded list.
- **Architecture**:
  - Built with LangGraph `StateGraph`, `START`, and conditional branching edges.
  - Cities supported: Mumbai, Delhi, Bengaluru, Ahmedabad, Hyderabad.
- **To Run**:
  ```bash
  python task3_zomato_langgraph.py
  ```
- **Test Scenarios**:
  - Multi-turn: User asks without city -> agent asks for city -> user replies "Mumbai" -> agent returns top 3 Mumbai restaurants.
  - Single-turn: User says "Suggest top restaurants in Bengaluru" -> agent directly returns top 3 Bengaluru restaurants.

---

### Task 4: BookMyShow Multi-Component Pipeline (LangChain + LangGraph)
- **Goal**: Chain LangChain (review summarization) and LangGraph (user interaction flow asking if more details are desired and displaying follow-up message).
- **Architecture**:
  - **Component 1 (LangChain)**: Summarizes critic review of *Kalki 2898 AD*.
  - **Component 2 (LangGraph)**:
    - Step 1: Delivers summary and asks: *"Would you like more details about cast, director, and trivia? (yes/no)"*
    - Branch A ("yes"): Displays full production details, star cast, and ticket booking info.
    - Branch B ("no"): Displays a polite farewell message.
- **To Run**:
  ```bash
  python task4_bms_langchain_langgraph_mcp.py
  ```

---

### Task 5: Twitter Trends Summarizer (AI Code Evolution)
- **Goal**: Analyze raw AI-generated code from ChatGPT / Copilot, fix deprecations/bugs, and summarize the top 2 trends from a mock Twitter API.
- **Documentation**: See [`task5_ai_code_evolution.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2015/task5_ai_code_evolution.md) for full before-and-after comparison.
- **Key Fixes Applied**:
  1. Replaced non-existent URL with local `MockTwitterAPI`.
  2. Upgraded deprecated `LLMChain` / `OpenAI` to modern LCEL (`prompt | llm | StrOutputParser`).
  3. Added sorting and strict slicing to top 2 trends (`sorted_trends[:2]`).
  4. Added deterministic local LLM fallback for zero-cost execution without API keys.
- **To Run**:
  ```bash
  python task5_twitter_trends_langchain.py
  ```
