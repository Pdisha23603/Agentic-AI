# SESSION 19 – Advanced Agentic Concepts (Part 2)

This repository contains the complete implementation, multi-agent communication architectures, agent refactoring designs, and workflow specifications for **Session 19: Advanced Agentic Concepts (Part 2)**.

---

## Overview of Tasks & Files Created

| Task | Topic | Files Created | Description |
| :--- | :--- | :--- | :--- |
| **Task 1** | Spotify Discover Weekly Agent | [`task1_spotify_discover_agent.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2019/task1_spotify_discover_agent.py) | Autonomous recommendation agent with clean modular separation into `perceive()`, `reason()`, and `act()` modules. |
| **Task 2** | Multi-Agent Movie Recommendation | [`task2_multi_agent_movie_system.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2019/task2_multi_agent_movie_system.py) | Multi-agent system where `MovieRecommendationAgent` communicates with `MovieDiscoveryAgent` via function calls to recommend movies. |
| **Task 3** | Refactored Restaurant Agent | [`task3_refactor_restaurant_agent.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2019/task3_refactor_restaurant_agent.py) | Refactored legacy monolithic function into a modular `AgentRestaurantRecommender` class with separate perception, reasoning, and action methods. |
| **Task 4** | Autonomous Food Delivery Workflow | [`task4_food_delivery_agentic_workflow.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2019/task4_food_delivery_agentic_workflow.md)<br>[`task4_delivery_agent_simulation.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2019/task4_delivery_agent_simulation.py) | Comprehensive 6-step agentic workflow design for Zomato/Swiggy ("NutriCraver Agent") + executable Python simulation. |

---

## Detailed Task Documentation & Execution

### Task 1: Spotify Discover Weekly Agent
- **Goal**: Recommend trending playlists based on listening history using Perception, Reasoning, and Action modules.
- **Architecture**:
  - `perceive(user_history)`: Ingests listening events, repeat counts, and skips to compute genre affinity weights.
  - `reason(perception_data)`: Matches user affinities against trending playlists, computing relevance scores.
  - `act(user_name, recommendations)`: Packages and delivers personalized Discover Weekly cards.
- **To Run**:
  ```bash
  python task1_spotify_discover_agent.py
  ```

---

### Task 2: Multi-Agent Movie Recommendation System
- **Goal**: Implement multi-agent communication via function calls between two specialized agents.
- **Agents**:
  - `MovieDiscoveryAgent`: Monitors new releases and exposes `fetch_latest_releases()`.
  - `MovieRecommendationAgent`: Invokes `MovieDiscoveryAgent` via function call, filters by user genres (`Sci-Fi`, `Action`, `Comedy`), and synthesizes recommendations.
- **To Run**:
  ```bash
  python task2_multi_agent_movie_system.py
  ```

---

### Task 3: Refactored Restaurant Recommender Agent
- **Goal**: Refactor legacy procedural code into an `AgentRestaurantRecommender` class.
- **Structure**:
  - `perceive(user_query)`: Extracts target cuisines, dietary requirements (`Pure Veg`), and budget constraints.
  - `reason(perception)`: Matches cuisines, enforces dietary & budget rules, and ranks candidates.
  - `act(ranked_candidates, perception)`: Formats presentation cards with signature dishes and action callouts.
- **To Run**:
  ```bash
  python task3_refactor_restaurant_agent.py
  ```

---

### Task 4: Autonomous Food Delivery Agentic Workflow
- **Selected Concept**: **NutriCraver Agent** (Context-Aware Dietary & Health Replenisher for Zomato/Swiggy).
- **The 6-Step Workflow**:
  1. *Contextual Perception*: Multi-sensor trigger (wearable health data + meeting calendar).
  2. *Reasoning & Restaurant Search*: Filters open restaurants within 3.5 km and matches target macros (protein, calories).
  3. *Cart Assembly & Customization*: Autonomous cart creation, dietary instructions, and coupon optimization.
  4. *Human-in-the-Loop Confirmation*: 1-tap push notification showing macro breakdown and arrival ETA.
  5. *Autonomous Order Execution*: Automated UPI payment and kitchen dispatch.
  6. *Active Telemetry & Reflection*: Live GPS rider tracking, weather mitigation, and post-meal rating feedback.
- **To Run Simulation**:
  ```bash
  python task4_delivery_agent_simulation.py
  ```
