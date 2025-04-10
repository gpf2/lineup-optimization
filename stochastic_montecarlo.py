import random
import numpy as np
from itertools import combinations
import json

#maybe compare past predicted points to past actual scores to see how much to
#weight the past_guess vs the current prediction
#also should try and do some optimization for weights
def simulate_player_score(player, week):
    for p in players:
        if p["name"]==player:
            break
    
    if week==1:
        base = (p["projected points"])[week-1]
    else:
        past_scores = p["scored points"][:week-1]
        mean = np.mean(past_scores)
        std_dev = np.std(past_scores)
        past_guess = max(np.random.normal(mean, std_dev/4), 0)

        projected = (p["projected points"])[week-1]
        base = 0.75*projected + 0.25*past_guess
    
    prob = random.random()
    if prob < p['boombust'][0]:
        return base*random.uniform(1.1, 1.2)
    elif prob < p['boombust'][1]:
        return base * random.uniform(0.8, 0.9)
    return base

def generate_valid_rosters(players):
    grouped_by_pos = dict()
    for position in ["QB", "RB", "WR", "TE", "DST", "K"]:
        position_players = []
        for p in players:
            if p["position"]==position:
                position_players.append(p)
        grouped_by_pos[position]=position_players

    rosters = []
    for qb in grouped_by_pos["QB"]:
        for rbs in combinations(grouped_by_pos["RB"], 2):
            for wrs in combinations(grouped_by_pos["WR"], 2):
                for te in grouped_by_pos['TE']:
                    for k in grouped_by_pos["K"]:
                        for dst in grouped_by_pos["DST"]:
                            seen = {qb["name"], (rbs[0])["name"], (rbs[1])["name"], 
                                       (wrs[0])["name"], (wrs[1])["name"], te["name"], 
                                       k["name"], dst["name"]}
                            flexes = []
                            for p in players:
                                if p["name"] not in seen and p["position"] in {"RB", "WR", "TE"}:
                                    flexes.append(p)
                            for flex in flexes:
                                roster = list(seen)
                                roster.append(flex["name"])
                                rosters.append(roster)
    return rosters

def monte_carlo_optimization(players, week):
    roster_scores = dict()
    valid_rosters = generate_valid_rosters(players)
    for roster in valid_rosters:
            roster_scores[tuple(roster)] = []

    for i in range(1000):
        print(f"Simulation {i}")
        for roster in valid_rosters:
            total_score = 0
            for p in roster:
                total_score+=simulate_player_score(p, week)
            roster_scores[tuple(roster)].append(total_score)

    best_roster = None
    best_score = -np.inf
    for roster, scores in roster_scores.items():
        score = np.mean(scores)
        if score>best_score:
            best_roster = roster
            best_score = score

    return best_roster, best_score

players = [
    {"name": "Jalen Hurts", "position": "QB"},
    {"name": "Tua Tagovailoa", "position": "QB"},

    {"name": "Christian McCaffrey", "position": "RB"},
    {"name": "Breece Hall", "position": "RB"},
    {"name": "De'Von Achane", "position": "RB"},
    {"name": "Isiah Pacheco", "position": "RB"},

    {"name": "CeeDee Lamb", "position": "WR"},
    {"name": "Chris Olave", "position": "WR"},
    {"name": "Christian Kirk", "position": "WR"},
    {"name": "George Pickens", "position": "WR"},

    {"name": "T.J. Hockenson", "position": "TE"},
    {"name": "Dalton Kincaid", "position": "TE"},

    {"name": "Baltimore Ravens", "position": "DST"},
    {"name": "Philadelphia Eagles", "position": "DST"},

    {"name": "Jake Elliott", "position": "K"},
    {"name": "Brandon McManus", "position": "K"}
]

with open('points.json', 'r') as file:
    data = json.load(file)
for p in players:
    p["projected points"] = data[p["name"]]

with open('weekly_fantasy_scores_2024.json', 'r') as file:
    data = json.load(file)

for key, value in data.items():
    points_scored = value["WeeklyPoints"]
    for i in range(1,len(points_scored), 1):
        if points_scored[str(i)]==None:
            points_scored[str(i)]=0.0

for p in players:
    info = (data[p["name"]])["WeeklyPoints"]
    scores = []
    for i in range(1,len(info), 1):
        scores.append(info[str(i)])
    p["scored points"] = scores

with open('boom_bust_2024.json', 'r') as file:
    data = json.load(file)

for p in players:
    if p["name"] in data:
        info = (data[p["name"]])["2024"]
        p["boombust"] = (info["Boom"], info["Bust"])
    else:
        p["boombust"] = (0,0)

#best_roster, best_score = monte_carlo_optimization(players, 3)
#print("Best roster:", best_roster)
#print("Expected avg score:", best_score)