import json
import numpy as np
from webscraping.weeklypoints import *
import os
import random

# Calculates the fantasy score for a given lineup during a specified week
# Provide a lineup in the following format
# lineup = ["Player Name", "Player Name", ...]
def calculate_lineup_score(lineup, year, week):
    json_path = f"json/weekly_fantasy_scores_{year}.json"
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

    return total_score

def get_total_projected_score(optimal):
    total = 0
    for i in optimal:
        total+=i["AdjustedScore"] 
    return total

def pick(pos, position_groups):
    return position_groups[pos].pop() if position_groups[pos] else None

# Generates a random fantasy roster during a specified year (Lineup + bench)
# Lineup constraints (9 players):
# 1 QB, 2 WR, 2 RB, 1 TE, 1 FLEX: WR/RB/TE, 1 DEF/ST, 1 K
# Bench constraints: 7 spots for any position
def generate_roster(year):
    json_path = f"json/weekly_fantasy_scores_{year}.json"

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
                roster.append(player)

    # 1 flex
    flex_pool = position_groups["RB"] + position_groups["WR"] + position_groups["TE"]
    random.shuffle(flex_pool)
    if flex_pool:
        flex = flex_pool.pop()
        for pos in ["RB", "WR", "TE"]:
            if flex in position_groups[pos]:
                position_groups[pos].remove(flex)
                break
        roster.append(flex)

    # Fill bench
    bench_needed = 16 - len(roster)
    bench_pool = []
    for pos, players in position_groups.items():
        bench_pool.extend([p for p in players])
    random.shuffle(bench_pool)
    roster.extend(bench_pool[:bench_needed])
    return roster

# Generates a random fantasy roster during a specified year (Lineup + bench)
# Roster constraints (16 players):
# 2 QB, 5 WR, 5 RB, 2 TE, 1 DEF/ST, 1 K
def generate_smart_roster(year):
    json_path = f"json/weekly_fantasy_scores_{year}.json"

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
        "QB": 2,
        "RB": 5,
        "WR": 5,
        "TE": 2,
        "K": 1,
        "DST": 1 
    }

    for pos, count in constraints.items():
        for _ in range(count):
            player = pick(pos, position_groups)
            if player:
                roster.append({player: {"Position": pos}})

    return roster

def weighted_avg(scores):
    weighted_sum = 0
    total_weight = 0
    for i, score in enumerate(reversed(scores)):
        weight = 0.75*(0.25)**i
        weighted_sum += weight*score
        total_weight += weight
    return weighted_sum/total_weight

#return 1 hot vector representing which players have a position in positions
def position_vector(positions, players):
    vector = []
    for name in list(players.keys()):
        if players[name]["position"] in positions:
            vector.append(1)
        else:
            vector.append(0)
    return vector

# create score vector for linear program objective function
def make_score_vector(players, week):
    assert(len(players)==16)
    names = list(players.keys())
    projected_points = []
    prev_scores = []
    weights = []

    for name in names:
        # get projected points for each player
        player = players[name]
        proj = player["projected points"][week-1]
        projected_points.append(proj)

        # get average past performance for each player
        if week > 1:
            guess = weighted_avg(player["prev season"]+player["scored points"][:week-1])
        else:
            guess = 0
        prev_scores.append(guess)
        base = proj*player["weights"][0] + guess*player["weights"][1]
        base = base + 5*(player['boombust'][0]-player['boombust'][1])
        
        # track projected, past, and guess for weight updates
        weights.append(player["weights"][:2])
        player["guessed scores"] = [proj, guess, base]
        
    projected_points = np.array(projected_points)
    prev_scores = np.array(prev_scores)
    weights = np.array(weights)

    # vector representing guess of what each player would score this week
    return weights[:,0]*projected_points + weights[:,1]*prev_scores

def generate_lineups(num_rosters):
    with open('json/weekly_fantasy_scores_2024.json', 'r') as file:
        data = json.load(file)


    generated_rosters = []
    positions = {'QB':2, 'RB':5, 'WR':5, 'TE':2, 'K':1, 'DST':1}

    player_dict = dict()
    for position in positions:
        player_dict[position]=[]
    for key, value in data.items():
        player_dict[value["Position"]].append(key)

    for i in range(num_rosters):
        roster = dict()
        for position in positions:
            possibilities = player_dict[position]

            for p in random.sample(possibilities, positions[position]):
                roster[p]={"position": position}
        generated_rosters.append(roster)
    return generated_rosters

def initialize_player_data(players):
    #add the projected points for each week to each players dictionary
    with open('json/points.json', 'r') as file:
        data = json.load(file)
    for p in players:
        players[p]["projected points"] = data[p]

    #add the actual scored points for each week to each players dictionary
    with open('json/weekly_fantasy_scores_2024.json', 'r') as file:
        data = json.load(file)
    #replace none values with 0
    for key, value in data.items():
        points_scored = value["WeeklyPoints"]
        for i in range(1,len(points_scored), 1):
            if points_scored[str(i)]==None:
                points_scored[str(i)]=0.0
    for p in players:
        info = (data[p])["WeeklyPoints"]
        scores = []
        for i in range(1,len(info), 1):
            scores.append(info[str(i)])
        players[p]["scored points"] = scores
    
    #add the past season scored points for each week to each players dictionary
    with open('json/weekly_fantasy_scores_2022.json', 'r') as file:
        data = json.load(file)
    #replace none values with 0
    for key, value in data.items():
        points_scored = value["WeeklyPoints"]
        for i in range(1,len(points_scored), 1):
            if points_scored[str(i)]==None:
                points_scored[str(i)]=0.0
    for p in players:
        if p in data:
            info = (data[p])["WeeklyPoints"]
            scores = []
            for i in range(1,len(info), 1):
                scores.append(info[str(i)])
            players[p]["prev season"] = scores
        else:
            players[p]["prev season"] = []
    with open('json/weekly_fantasy_scores_2023.json', 'r') as file:
        data = json.load(file)
    for key, value in data.items():
        points_scored = value["WeeklyPoints"]
        for i in range(1,len(points_scored), 1):
            if points_scored[str(i)]==None:
                points_scored[str(i)]=0.0
    for p in players:
        if p in data:
            info = (data[p])["WeeklyPoints"]
            scores = []
            for i in range(1,len(info), 1):
                scores.append(info[str(i)])
            players[p]["prev season"] += scores
        elif "prev season" not in players[p]:
            print(1)
            players[p]["prev season"] = []

    #add the boombust each players dictionary
    #initialize the weights and the score trackers
    with open('json/boom_bust_2024.json', 'r') as file:
        data = json.load(file)
    for p in players:
        if p in data:
            info = (data[p])["2024"]
            players[p]["boombust"] = (info["Boom"], info["Bust"])
        else:
            players[p]["boombust"] = (0,0)
        players[p]["weights"] = [0.5, 0.5, 1.1, 0.9]
        players[p]["guessed scores"] = [0, 0, 0]
    return players
