import json
import cvxpy as cp
import numpy as np

def pos_count(pos, positions, n, x):
        return cp.sum([x[i] for i in range(n) if positions[i] == pos])

# LP using Simplex Method & Branch and Bound
def optimize_lineup_simplex(roster, year, week, w1, w2, w3, base_consistency):
    projected_path = "json/points.json"
    bust_path = "json/boom_bust_2024.json"
    actual_path = "json/weekly_fantasy_scores_2024.json"
    year = str(year)
    week = int(week)

    with open(projected_path) as f:
        projected_points = json.load(f)

    with open(bust_path) as f:
        boom_bust = json.load(f)

    with open(actual_path) as f:
        actual_scores = json.load(f)

    valid_players = []
    positions = []
    adj_scores = []

    for player in roster:
        # Make sure players have same name across files
        if player not in projected_points or player not in actual_scores:
            print(player, "not in one of the json files")
            continue

        try:
            proj_pts = projected_points[player][week - 1]
        except (IndexError, KeyError, TypeError):
            proj_pts = 0

        act_info = actual_scores[player]
        position = act_info.get("Position", None)
        week_scores = act_info.get("WeeklyPoints", {})

        # Past scores heuristic
        past_scores = [
            score for w, score in week_scores.items()
            if score is not None and int(w) < week
        ]
        avg_past_score = np.mean(past_scores) if past_scores else 0

        # Consistency heuristic
        if player in boom_bust and position in ["QB", "RB", "WR", "TE"]:
            bust_info = boom_bust[player].get(year, {})
            consistency = bust_info.get("Consistency", base_consistency)
        else:
            consistency = base_consistency 

        # Weighted score
        adjusted = w1 * proj_pts + w2 * avg_past_score + w3 * consistency * proj_pts

        valid_players.append(player)
        positions.append(position)
        adj_scores.append(adjusted)

    n = len(valid_players)
    # players not all valid (mismatched names between the jsons)
    if n < 9:
        return
    
    x = cp.Variable(n, boolean=True)
    objective = cp.Maximize(cp.sum(cp.multiply(x, adj_scores)))
    constraints = []
    # lineup position counts
    constraints += [
        pos_count("QB", positions, n, x) == 1,
        pos_count("RB", positions, n, x) >= 2,
        pos_count("WR", positions, n, x) >= 2,
        pos_count("TE", positions, n, x) >= 1,
        pos_count("K", positions, n, x) == 1,
        pos_count("DST", positions, n, x) == 1,
        cp.sum(x) == 9
    ]

    problem = cp.Problem(objective, constraints)
    #problem.solve(solver=cp.GLPK_MI, verbose=True)
    problem.solve(solver=cp.GLPK_MI)

    if x.value is None:
        return "error"
    res = []
    for i in range(n):
        if x.value[i] == 1:
            player_entry = {
                "Player": valid_players[i],
                "AdjustedScore": float(round(adj_scores[i], 2))
            }
            res.append(player_entry)

    return res



