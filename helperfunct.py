import json
from weeklypoints import *
import os

def calculate_lineup_score(lineup, json_path, year, week):
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
