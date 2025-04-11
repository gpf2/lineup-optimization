import random
import numpy as np
from itertools import combinations
import json

num_iterations = 1000

#maybe compare past predicted points to past actual scores to see how much to
#weight the past_guess vs the current prediction
#also should try and do some optimization for weights
def simulate_player_score(player, week):
    p = players[player]
    
    #if its the first week, only account for the projected points
    if week==1:
        base = (p["projected points"])[week-1]
        past_guess = None
        projected = base
    #otherwise, combine past performance this season and the projected points
    else:
        past_scores = p["scored points"][:week-1]
        mean = np.mean(past_scores)
        std_dev = np.std(past_scores)
        #take a random var from a normal distribution of the past performances
        #this season
        past_guess = max(np.random.normal(mean, std_dev), 0)

        #take a combo of the projected points and the past performance
        projected = (p["projected points"])[week-1]
        base = p["weights"][0]*projected + p["weights"][1]*past_guess
    
    prob = random.random()
    #if boom, scale the base up a little
    if prob < p['boombust'][0]:
        return projected, past_guess, base*random.uniform(p["weights"][2], p["weights"][2]+0.1)
    #if boom, scale the base down a little
    elif prob < p['boombust'][1]:
        return projected, past_guess, base * random.uniform(p["weights"][3], p["weights"][3]+0.1)
    return projected, past_guess, base

def generate_valid_rosters(players):
    grouped_by_pos = dict()
    #create a dict mapping position to list of posisble players
    for position in ["QB", "RB", "WR", "TE", "DST", "K"]:
        position_players = []
        for p in players:
            if players[p]["position"]==position:
                position_players.append(p)
        grouped_by_pos[position]=position_players

    rosters = []
    #create all possible combos of rosters
    for qb in grouped_by_pos["QB"]:
        for rbs in combinations(grouped_by_pos["RB"], 2):
            for wrs in combinations(grouped_by_pos["WR"], 2):
                for te in grouped_by_pos['TE']:
                    for k in grouped_by_pos["K"]:
                        for dst in grouped_by_pos["DST"]:
                            seen = {qb, rbs[0], rbs[1], wrs[0], wrs[1], te, k, dst}
                            flexes = []
                            #pick leftover valid flexes
                            for p in players:
                                if p not in seen and players[p]["position"] in {"RB", "WR", "TE"}:
                                    flexes.append(p)
                            for flex in flexes:
                                roster = list(seen)
                                roster.append(flex)
                                rosters.append(roster)
    return rosters

def monte_carlo_optimization(players, week):
    #get valid rosters and initialize score tracker
    roster_scores = dict()
    valid_rosters = generate_valid_rosters(players)
    for roster in valid_rosters:
            roster_scores[tuple(roster)] = []

    for i in range(num_iterations):
        #score each roster 
        for roster in valid_rosters:
            total_score = 0
            for p in roster:
                proj, guess, score = simulate_player_score(p, week)
                #track the projected/past guess score for weight updates
                if week!=1:
                    players[p]["guessed scores"][0] += proj
                    players[p]["guessed scores"][1] += guess
                    players[p]["guessed scores"][2] += score
                total_score+=score
            roster_scores[tuple(roster)].append(total_score)

    #determine the best roster from the avg score over all iterations
    best_roster = None
    best_score = -np.inf
    for roster, scores in roster_scores.items():
        score = np.mean(scores)
        if score>best_score:
            best_roster = roster
            best_score = score

    return best_roster, best_score, valid_rosters

players = {
    "Jalen Hurts": {"position": "QB"},
    "Tua Tagovailoa": {"position": "QB"},

    "Christian McCaffrey": {"position": "RB"},
    "Breece Hall": {"position": "RB"},
    "De'Von Achane": {"position": "RB"},
    "Isiah Pacheco": {"position": "RB"},

    "CeeDee Lamb": {"position": "WR"},
    "Chris Olave": {"position": "WR"},
    "Christian Kirk": {"position": "WR"},
    "George Pickens": {"position": "WR"},

    "T.J. Hockenson": {"position": "TE"},
    "Dalton Kincaid": {"position": "TE"},

    "Baltimore Ravens": {"position": "DST"},
    "Philadelphia Eagles": {"position": "DST"},

    "Jake Elliott" : {"position": "K"},
    "Brandon McManus" : {"position": "K"},
}

#add the projected points for each week to each players dictionary
with open('points.json', 'r') as file:
    data = json.load(file)
for p in players:
    players[p]["projected points"] = data[p]

#add the actual scored points for each week to each players dictionary
with open('weekly_fantasy_scores_2024.json', 'r') as file:
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

#add the boombust each players dictionary
#initialize the weights and the score trackers
with open('boom_bust_2024.json', 'r') as file:
    data = json.load(file)
for p in players:
    if p in data:
        info = (data[p])["2024"]
        players[p]["boombust"] = (info["Boom"], info["Bust"])
    else:
        players[p]["boombust"] = (0,0)
    players[p]["weights"] = [0.5, 0.5, 1.1, 0.8]
    players[p]["guessed scores"] = [0, 0, 0]
