import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helperfunct import *

lineup = [
    "Lamar Jackson",
    "Ja'Marr Chase",
    "Josh Allen",
    "Joe Burrow",
    "Baker Mayfield",
    "Jayden Daniels"
]
score, breakdown = calculate_lineup_score(lineup, "weekly_fantasy_scores_2024.json", year=2024, week=1)

print("Total Score:", score)
print("Breakdown:")
for player, points in breakdown.items():
    print(f" - {player}: {points}")
