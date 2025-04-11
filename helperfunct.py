import json
from project.webscraping.weeklypoints import *
import os
import random

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

def pick(pos, position_groups):
    return position_groups[pos].pop() if position_groups[pos] else None

# Generates a random fantasy roster during a specified year (Lineup + bench)
# Lineup constraints (9 players):
# 1 QB, 2 WR, 2 RB, 1 TE, 1 FLEX: WR/RB/TE, 1 DEF/ST, 1 K
# Bench constraints: 7 spots for any position
def generate_roster(year):
    json_path = f"weekly_fantasy_scores_{year}.json"

    if not os.path.exists(json_path):
        print(f"Scraping weekly scores for {year}")
        data = scrape_weekly_scores(year)
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        
    with open(json_path, "r") as f:
        data = json.load(f)

    position_groups = {"QB": [], "RB": [], "WR": [], "TE": [], "K": [], "DST": []}
    for player, info in data.items():
        pos = info.get("Position")
        if pos in position_groups:
            position_groups[pos].append(player)

    for players in position_groups.values():
        random.shuffle(players)

    roster = []

    # Lineup constraints
    constraints = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "K": 1,
        "DST": 1 
    }

    for pos, count in constraints.items():
        for _ in range(count):
            player = pick(pos, position_groups)
            if player:
                roster.append({player: {"Position": pos}})

    # 1 flex
    flex_pool = position_groups["RB"] + position_groups["WR"] + position_groups["TE"]
    random.shuffle(flex_pool)
    if flex_pool:
        flex_pick = flex_pool.pop()
        for pos in ["RB", "WR", "TE"]:
            if flex_pick in position_groups[pos]:
                position_groups[pos].remove(flex_pick)
                break
        roster.append({flex_pick: {"Position": pos}})

    # Fill bench
    bench_needed = 16 - len(roster)
    bench_pool = []
    for pos, players in position_groups.items():
        bench_pool.extend([{p: {"Position": pos}} for p in players])
    random.shuffle(bench_pool)
    roster.extend(bench_pool[:bench_needed])
    return {"Roster": roster}

# Generates a random fantasy roster during a specified year (Lineup + bench)
# Lineup constraints (9 players):
# 1 QB, 2 WR, 2 RB, 1 TE, 1 FLEX: WR/RB/TE, 1 DEF/ST, 1 K
# Bench constraints: 1 QB, 2/3 WR, 2/3 RB, 0/1 TE
def generate_smart_roster(year):
    json_path = f"weekly_fantasy_scores_{year}.json"

    if not os.path.exists(json_path):
        print(f"Scraping weekly scores for {year}")
        data = scrape_weekly_scores(year)
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    with open(json_path, "r") as f:
        data = json.load(f)

    position_groups = {"QB": [], "RB": [], "WR": [], "TE": [], "K": [], "DST": []}
    for player, info in data.items():
        pos = info.get("Position")
        avg = info.get("AVG", 0)
        if pos in position_groups and avg > 0:
            position_groups[pos].append(player)

    for players in position_groups.values():
        random.shuffle(players)

    roster = []

    # Lineup constraints
    constraints = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "K": 1,
        "DST": 1 
    }

    for pos, count in constraints.items():
        for _ in range(count):
            player = pick(pos, position_groups)
            if player:
                roster.append({player: {"Position": pos}})

    # 1 flex
    flex_pool = position_groups["RB"] + position_groups["WR"] + position_groups["TE"]
    random.shuffle(flex_pool)
    if flex_pool:
        flex_pick = flex_pool.pop()
        for pos in ["RB", "WR", "TE"]:
            if flex_pick in position_groups[pos]:
                position_groups[pos].remove(flex_pick)
                break
        roster.append({flex_pick: {"Position": pos}})

    # Fill bench
    bench = []
    TE_amt = random.choice([0, 1])
    if TE_amt == 0:
        WR_amt = 3
        RB_amt = 3
    else:
        WR_amt = random.choice([2, 3])
        RB_amt = 5-WR_amt
    bench_constraints = {
        "QB": 1,
        "TE": TE_amt,
        "WR": WR_amt,
        "RB": RB_amt
    }

    for pos, count in bench_constraints.items():
        for _ in range(count):
            player = pick(pos, position_groups)
            if player:
                bench.append({player: {"Position": pos}})

    roster.extend(bench)
    return {"Roster": roster}
