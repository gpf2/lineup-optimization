import json
from weeklypoints import *
import os

# Calculates the fantasy score for a given lineup during a specified week
# Provide a lineup in the following format
# lineup = ["Player Name", "Player Name", ...]
def calculate_lineup_score(lineup, year, week):
    json_path = f"weekly_fantasy_scores_{year}.json"
    if not os.path.exists(json_path):
        print(f"Scraping weekly scores for {year}")
        data = scrape_weekly_scores(year)
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        
    with open(json_path, "r") as f:
        data = json.load(f)

    week = str(week) 
    year = str(year)

    total_score = 0.0
    breakdown = {}

    print(f"Calculating lineup fantasy score for week {week}")
    for player in lineup:
        if player not in data:
            breakdown[player] = "Not found"
            continue

        player_data = data[player]
        if str(player_data.get("Year")) != year:
            breakdown[player] = "Year mismatch"
            continue

        weekly_points = player_data.get("WeeklyPoints", {})
        score = weekly_points.get(week)

        if score is None:
            breakdown[player] = "No score (BYE or DNP)"
        else:
            total_score += score
            breakdown[player] = score

    return total_score, breakdown


# Generates a random fantasy roster during a specified year (Lineup + bench)
# constraints for lineup (9 players):
# 1 QB
# 2 WR
# 2 RB
# 1 TE
# 1 FLEX: WR/RB/TE
# 1 DEF/ST
# 1 K
# Bench constraints (7 players):
# 7 spots for any position
# usually 1 QB, 2/3 WR, 2/3 RB, 0/1 TE
# so roster should have 16 players

# This will generate a fully random bench TODO
def generate_random_roster(year):
    return

# This will generate a bench based on typical constraints TODO
def generate_roster(year):
    return
