# ============================================
# Task 3: IPL Match Multi-Agent System
# ============================================

# Agent 1 - Fetch IPL Scores
def fetch_ipl_scores():
    print("Agent 1: Fetching IPL match scores...\n")

    scores = {
        "RCB": 198,
        "CSK": 176,
        "MI": 210,
        "GT": 189
    }

    return scores


# Agent 2 - Calculate Highest Score
def highest_team_score(scores):
    print("Agent 2: Finding highest scoring team...\n")

    team = max(scores, key=scores.get)
    score = scores[team]

    return {
        "team": team,
        "score": score,
        "all_scores": scores
    }


# Agent 3 - Generate Report
def print_score_report(result):
    print("===== IPL MATCH REPORT =====")

    for team, score in result["all_scores"].items():
        print(f"{team} : {score}")

    print("---------------------------")
    print("Highest Score :", result["team"])
    print("Runs          :", result["score"])


# Multi-Agent Workflow
match_scores = fetch_ipl_scores()
highest_score = highest_team_score(match_scores)
print_score_report(highest_score)