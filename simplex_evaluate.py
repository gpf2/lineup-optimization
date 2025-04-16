from linear_simplex import optimize_lineup_simplex
from helperfunct import calculate_lineup_score, get_total_projected_score, generate_roster
from itertools import product
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

def eval_simplex():
    diff = []
    for _ in range(10):
        roster = generate_roster(2024)
        for week in range(1,16):
            res = optimize_lineup_simplex(roster, 2024, week, .4,.4,.2, 0.85)
            lineup = []
            for j in res:
                lineup.append(j["Player"])
            projected = get_total_projected_score(res)
            actual = calculate_lineup_score(lineup, 2024, week)
            print(f"projected score: {projected}")
            print(f"actual score: {actual}")
            diff.append(abs(projected-actual))
    print(f"avg diff: {sum(diff)/(len(diff))}")
    return
eval_simplex()

def eval_simplex_weights():
    best_weights_per_week = {}
    all_results = defaultdict(list)
    
    weights = [(w1, w2, 1.0 - w1 - w2)
                   for w1, w2 in product([i * 0.1 for i in range(11)], repeat=2)
                   if 0 <= 1.0 - w1 - w2 <= 1.0]

    for week in range(1, 16):
        print(f"\n week {week}...")
        best_diff = float("inf")
        best_weights = None
        for w1, w2, w3 in weights:
            diffs = []
            for _ in range(30): 
                roster = generate_roster(2024)
                res = optimize_lineup_simplex(roster, 2024, week, w1, w2, w3)
                if res == "error" or res is None:
                    continue
                lineup = [j["Player"] for j in res]
                projected = get_total_projected_score(res)
                actual = calculate_lineup_score(lineup, 2024, week)
                if projected is not None and actual is not None:
                    diffs.append(abs(projected - actual))
            if diffs:
                avg_diff = sum(diffs) / len(diffs)
                all_results[week].append((w1, w2, w3, avg_diff))
                if avg_diff < best_diff:
                    best_diff = avg_diff
                    best_weights = (w1, w2, w3)
        best_weights_per_week[week] = (best_weights, best_diff)
        print(f"{week} best: w1={best_weights[0]}, w2={best_weights[1]}, w3={best_weights[2]}, avg diff: {best_diff:.4f}")

    return best_weights_per_week, all_results
