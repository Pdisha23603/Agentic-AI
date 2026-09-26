# Session 20 - Task 4: AI Code Generation & Engineering Notes

This document records the prompt used to generate the IPL multi-agent system code via an LLM (ChatGPT / Claude / Copilot), the raw generated code, the engineering review, the bugs/limitations identified, and the modifications implemented to make it production-ready.

---

## 1. The Prompt Used

```text
Act as an expert Python AI engineer. Write a simple multi-agent system in Python consisting of two agents:
1. IPLScoreAgent: Simulates fetching live or recent IPL cricket match scores from a static database or API.
2. MatchSummaryAgent: Takes the match data from the score agent and generates a concise, human-readable commentary summary.
Show how the two agents communicate to deliver the summary for an IPL match.
```

---

## 2. Raw LLM-Generated Code (Initial Prototype)

```python
# Raw AI-generated code from ChatGPT prompt
class IPLScoreAgent:
    def __init__(self):
        self.scores = {
            "CSK vs MI": {
                "team1": "CSK", "score1": "206/4",
                "team2": "MI", "score2": "186/6",
                "winner": "CSK"
            }
        }
    def get_score(self, match):
        return self.scores[match]

class MatchSummaryAgent:
    def summarize(self, data):
        summary = f"Match: {data['team1']} scored {data['score1']} and {data['team2']} scored {data['score2']}. {data['winner']} won the match!"
        return summary

# Test
fetcher = IPLScoreAgent()
summarizer = MatchSummaryAgent()
data = fetcher.get_score("CSK vs MI")
print(summarizer.summarize(data))
```

---

## 3. Code Review & Gaps Analysis

While the raw generated snippet provides the most basic proof-of-concept, it has severe architectural and practical flaws when tested in a real environment:

| Category | Raw AI Code Limitation | Why It Fails in Practice |
| :--- | :--- | :--- |
| **Error Handling** | Direct dict indexing `self.scores[match]` | Raises an unhandled `KeyError` if an invalid match is queried. |
| **Telemetry Depth** | Only 3 flat string keys (`score1`, `score2`, `winner`) | Completely misses individual player contributions, overs bowled, wickets, venues, and ball-by-ball context. |
| **Match States** | Assumes every match is completed with a winner | Cannot handle live matches in progress (e.g. 2nd innings chase requiring RRR calculation). |
| **Mathematical Reasoning** | Pure string concatenation | Agents should demonstrate cognitive reasoning — computing Current Run Rate (CRR), Required Run Rate (RRR), and balls remaining. |
| **Windows Console Safety** | No stdout encoding reconfiguration | Crashes with `UnicodeEncodeError` on Windows `cp1252` when sports symbols or emojis are introduced. |
| **Type Safety & Modularity** | No typing annotations or structured payloads | Brittle inter-agent communication contract prone to silent breakage. |

---

## 4. Changes & Enhancements Made

To transform the prototype into a production-grade multi-agent architecture in [`task4_ipl_multi_agent.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2020/task4_ipl_multi_agent.py):

1. **Standardized Inter-Agent Contract**:
   - `CricketScoreAgent.get_live_scores(match_id)` returns a standardized envelope:
     ```python
     {"status": "success" | "error", "data": {...}, "message": "..."}
     ```
2. **Dynamic Run Rate & Chase Equations**:
   - Implemented dynamic calculation of Current Run Rate ($CRR = \frac{\text{Runs}}{\text{Overs}}$).
   - For live matches (`status == 'LIVE_CHASE'`), dynamically computes balls bowled, balls remaining, runs needed, and Required Run Rate ($RRR = \frac{\text{Runs Needed}}{\text{Balls Remaining} / 6}$).
3. **Rich Match Datasets**:
   - Expanded catalog to include distinct match scenarios:
     - Completed high-scoring derby (CSK vs MI, El Clasico).
     - Live 2nd innings chase (RCB vs KKR at Chinnaswamy).
     - Last-ball 3-wicket thriller (GT vs RR).
4. **Resilient Error Boundaries**:
   - Safe lookup with descriptive error payload if an invalid or expired match ID is provided.
5. **Windows UTF-8 Encoding**:
   - Added `sys.stdout.reconfigure(encoding="utf-8")` to guarantee flawless execution across all terminals.

---

## 5. Verification & Test Results

The refactored script was executed via terminal:
```bash
python "Assignment/Session 20/task4_ipl_multi_agent.py"
```

**Results**:
- Successfully listed available matches.
- Handled completed matches with Player of the Match and final margin.
- Handled live chase matches with dynamic balls-remaining and RRR math.
- Gracefully handled invalid match queries without throwing exceptions.
- Exit code: `0` (Clean pass).
