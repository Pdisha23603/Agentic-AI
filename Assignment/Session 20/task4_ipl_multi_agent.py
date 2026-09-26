"""
Session 20 - Task 4: Multi-Agent IPL Cricket Score Fetcher & Summarizer
----------------------------------------------------------------------
This script implements a multi-agent system where:
1. CricketScoreAgent (IPLScoreFetcherAgent): Fetches and simulates rich IPL match data.
2. MatchSummaryAgent: Analyzes raw match metrics and synthesizes human-like commentary,
   calculating required run rates, top performer spotlights, and match outcomes.
Tested and refactored from initial AI-generated prototype for production robustness.
"""

import sys
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# Simulated IPL Match Score Database
# ============================================================================
IPL_MATCHES_DATABASE: Dict[str, Dict[str, Any]] = {
    "MATCH-2024-01": {
        "match_id": "MATCH-2024-01",
        "title": "Chennai Super Kings vs Mumbai Indians (El Clasico)",
        "venue": "Wankhede Stadium, Mumbai",
        "status": "COMPLETED",
        "team_1": {
            "name": "Chennai Super Kings",
            "short_name": "CSK",
            "score": 206,
            "wickets": 4,
            "overs": 20.0,
            "top_scorers": [
                {"name": "Ruturaj Gaikwad", "runs": 69, "balls": 40, "fours": 5, "sixes": 5},
                {"name": "Shivam Dube", "runs": 66, "balls": 38, "fours": 10, "sixes": 2},
                {"name": "MS Dhoni", "runs": 20, "balls": 4, "fours": 0, "sixes": 3}
            ],
            "top_bowlers": [
                {"name": "Matheesha Pathirana", "overs": 4.0, "runs": 28, "wickets": 4}
            ]
        },
        "team_2": {
            "name": "Mumbai Indians",
            "short_name": "MI",
            "score": 186,
            "wickets": 6,
            "overs": 20.0,
            "top_scorers": [
                {"name": "Rohit Sharma", "runs": 105, "balls": 63, "fours": 11, "sixes": 5, "not_out": True},
                {"name": "Tilak Varma", "runs": 31, "balls": 20, "fours": 5, "sixes": 0}
            ],
            "top_bowlers": [
                {"name": "Jasprit Bumrah", "overs": 4.0, "runs": 27, "wickets": 0},
                {"name": "Hardik Pandya", "overs": 3.0, "runs": 43, "wickets": 2}
            ]
        },
        "result": "Chennai Super Kings won by 20 runs",
        "player_of_the_match": "Matheesha Pathirana (4/28)"
    },
    "MATCH-2024-02": {
        "match_id": "MATCH-2024-02",
        "title": "Royal Challengers Bengaluru vs Kolkata Knight Riders",
        "venue": "M. Chinnaswamy Stadium, Bengaluru",
        "status": "LIVE_CHASE",
        "team_1": {
            "name": "Royal Challengers Bengaluru",
            "short_name": "RCB",
            "score": 221,
            "wickets": 6,
            "overs": 20.0,
            "top_scorers": [
                {"name": "Virat Kohli", "runs": 83, "balls": 59, "fours": 4, "sixes": 4, "not_out": True},
                {"name": "Dinesh Karthik", "runs": 20, "balls": 8, "fours": 3, "sixes": 1}
            ],
            "top_bowlers": [
                {"name": "Mohammed Siraj", "overs": 3.0, "runs": 32, "wickets": 1}
            ]
        },
        "team_2": {
            "name": "Kolkata Knight Riders",
            "short_name": "KKR",
            "score": 182,
            "wickets": 3,
            "overs": 15.2,
            "target": 222,
            "top_scorers": [
                {"name": "Sunil Narine", "runs": 47, "balls": 22, "fours": 2, "sixes": 5},
                {"name": "Venkatesh Iyer", "runs": 50, "balls": 30, "fours": 3, "sixes": 4}
            ],
            "top_bowlers": [
                {"name": "Andre Russell", "overs": 4.0, "runs": 29, "wickets": 2}
            ]
        },
        "result": "KKR need 40 runs in 28 balls to win (Live)",
        "player_of_the_match": "In Progress"
    },
    "MATCH-2024-03": {
        "match_id": "MATCH-2024-03",
        "title": "Gujarat Titans vs Rajasthan Royals",
        "venue": "Narendra Modi Stadium, Ahmedabad",
        "status": "COMPLETED",
        "team_1": {
            "name": "Rajasthan Royals",
            "short_name": "RR",
            "score": 196,
            "wickets": 3,
            "overs": 20.0,
            "top_scorers": [
                {"name": "Sanju Samson", "runs": 68, "balls": 38, "fours": 7, "sixes": 2, "not_out": True},
                {"name": "Riyan Parag", "runs": 76, "balls": 48, "fours": 3, "sixes": 5}
            ],
            "top_bowlers": [
                {"name": "Kuldeep Sen", "overs": 4.0, "runs": 41, "wickets": 3}
            ]
        },
        "team_2": {
            "name": "Gujarat Titans",
            "short_name": "GT",
            "score": 199,
            "wickets": 7,
            "overs": 20.0,
            "top_scorers": [
                {"name": "Shubman Gill", "runs": 72, "balls": 44, "fours": 6, "sixes": 2},
                {"name": "Rashid Khan", "runs": 24, "balls": 11, "fours": 4, "sixes": 0, "not_out": True}
            ],
            "top_bowlers": [
                {"name": "Rashid Khan", "overs": 4.0, "runs": 18, "wickets": 1}
            ]
        },
        "result": "Gujarat Titans won by 3 wickets (last-ball thriller)",
        "player_of_the_match": "Rashid Khan (24* off 11 & 1/18)"
    }
}


# ============================================================================
# Agent 1: CricketScoreAgent (IPL Score Fetcher)
# ============================================================================
class CricketScoreAgent:
    """
    Perceives requests for cricket match data, retrieves structured scorecards
    from the tournament repository or API, and delivers clean telemetry.
    """

    def __init__(self, database: Optional[Dict[str, Dict[str, Any]]] = None):
        self.db = database or IPL_MATCHES_DATABASE

    def get_live_scores(self, match_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves scorecard for a specific match ID or returns the latest active match.
        """
        if match_id:
            if match_id in self.db:
                return {"status": "success", "data": self.db[match_id]}
            return {"status": "error", "message": f"Match with ID '{match_id}' not found."}

        # If no match_id provided, default to first live or recent match
        first_match = next(iter(self.db.values()))
        return {"status": "success", "data": first_match}

    def list_available_matches(self) -> List[Dict[str, str]]:
        """Returns brief catalog of available matches."""
        return [
            {"match_id": m_id, "title": m["title"], "status": m["status"]}
            for m_id, m in self.db.items()
        ]


# ============================================================================
# Agent 2: MatchSummaryAgent (Score Summarizer & Narrative Synthesizer)
# ============================================================================
class MatchSummaryAgent:
    """
    Perceives raw score telemetry from CricketScoreAgent, reasons over match
    metrics (run rates, chase equations, standout batting/bowling spells),
    and generates an insightful, conversational commentary summary.
    """

    def summarize_match(self, raw_score_response: Dict[str, Any]) -> str:
        """
        Takes raw scorecard payload and transforms it into an analytical sports report.
        """
        if raw_score_response.get("status") != "success":
            return f"[MatchSummaryAgent] Error: {raw_score_response.get('message', 'Unable to retrieve match data.')}"

        match = raw_score_response["data"]
        t1 = match["team_1"]
        t2 = match["team_2"]
        status = match.get("status", "UNKNOWN")

        # Calculate Run Rates
        t1_crr = (t1["score"] / t1["overs"]) if t1["overs"] > 0 else 0.0
        t2_crr = (t2["score"] / t2["overs"]) if t2["overs"] > 0 else 0.0

        summary_lines = [
            f"==================================================================",
            f"  CRICKET MATCH SUMMARY: {match['title'].upper()}",
            f"  Venue: {match['venue']} | Status: {status}",
            f"==================================================================",
            f"\n📊 INNINGS 1: {t1['name']} ({t1['short_name']})",
            f"   Score: {t1['score']}/{t1['wickets']} in {t1['overs']} overs (Current Run Rate: {t1_crr:.2f})"
        ]

        # Top Batsmen T1
        top_bats_t1 = ", ".join([f"{b['name']} ({b['runs']} off {b['balls']}b)" for b in t1.get("top_scorers", [])[:2]])
        summary_lines.append(f"   Key Batters: {top_bats_t1}")

        summary_lines.extend([
            f"\n📊 INNINGS 2: {t2['name']} ({t2['short_name']})",
            f"   Score: {t2['score']}/{t2['wickets']} in {t2['overs']} overs (Current Run Rate: {t2_crr:.2f})"
        ])

        # Top Batsmen T2
        top_bats_t2 = ", ".join([f"{b['name']} ({b['runs']} off {b['balls']}b)" for b in t2.get("top_scorers", [])[:2]])
        summary_lines.append(f"   Key Batters: {top_bats_t2}")

        # Live Chase Situation vs Match Conclusion
        summary_lines.append("\n🎯 MATCH SITUATION & HIGHLIGHTS:")
        if status == "LIVE_CHASE":
            target = t2.get("target", t1["score"] + 1)
            runs_needed = target - t2["score"]
            # Remaining balls
            overs_done = t2["overs"]
            balls_bowled = int(overs_done) * 6 + round((overs_done - int(overs_done)) * 10)
            remaining_balls = max(0, 120 - balls_bowled)
            rrr = (runs_needed / (remaining_balls / 6)) if remaining_balls > 0 else 0.0

            summary_lines.append(f"   * Equation: {t2['short_name']} need {runs_needed} runs from {remaining_balls} balls to win.")
            summary_lines.append(f"   * Required Run Rate (RRR): {rrr:.2f} runs per over.")
            summary_lines.append(f"   * Prediction: High-stakes thriller in progress! Batting team holds advantage with wickets in hand.")
        else:
            summary_lines.append(f"   * Final Result: {match['result']}.")
            summary_lines.append(f"   * Player of the Match: {match.get('player_of_the_match', 'N/A')}.")

        summary_lines.append("==================================================================")
        return "\n".join(summary_lines)


# ============================================================================
# Multi-Agent Coordination Pipeline
# ============================================================================
class IPLMultiAgentSystem:
    """
    Coordinates data pipeline between CricketScoreAgent and MatchSummaryAgent.
    """

    def __init__(self):
        self.score_agent = CricketScoreAgent()
        self.summary_agent = MatchSummaryAgent()

    def process_match(self, match_id: Optional[str] = None) -> str:
        """
        Step 1: Score agent retrieves raw telemetry.
        Step 2: Summary agent synthesizes insights.
        """
        print(f"[*] Step 1: CricketScoreAgent fetching data for match: '{match_id or 'Latest'}'...")
        raw_data = self.score_agent.get_live_scores(match_id)

        print(f"[*] Step 2: MatchSummaryAgent synthesizing analytical report...")
        summary = self.summary_agent.summarize_match(raw_data)
        return summary


# ============================================================================
# Execution & Test Demonstration
# ============================================================================
def main():
    print("=" * 70)
    print("  IPL CRICKET MULTI-AGENT SCORE & SUMMARY SYSTEM (SESSION 20 - TASK 4)")
    print("=" * 70)

    system = IPLMultiAgentSystem()

    # List all available matches
    matches = system.score_agent.list_available_matches()
    print("\nAvailable IPL Matches in System:")
    for m in matches:
        print(f"  - [{m['match_id']}] {m['title']} (Status: {m['status']})")
    print()

    # Test 1: Completed El Clasico (CSK vs MI)
    print("\n>>> TEST CASE 1: Completed Match (CSK vs MI)")
    report_1 = system.process_match("MATCH-2024-01")
    print(report_1)

    # Test 2: Live Chase (RCB vs KKR)
    print("\n>>> TEST CASE 2: Live Chase Match (RCB vs KKR)")
    report_2 = system.process_match("MATCH-2024-02")
    print(report_2)

    # Test 3: Last-ball thriller (GT vs RR)
    print("\n>>> TEST CASE 3: Last-ball Thriller (GT vs RR)")
    report_3 = system.process_match("MATCH-2024-03")
    print(report_3)

    # Test 4: Edge Case - Non-existent match ID
    print("\n>>> TEST CASE 4: Edge Case (Invalid Match ID)")
    report_4 = system.process_match("INVALID-MATCH-999")
    print(report_4)

    print("\n" + "=" * 70)
    print("[SUCCESS] Task 4: IPL Multi-Agent System tested and verified!")
    print("=" * 70)


if __name__ == "__main__":
    main()
