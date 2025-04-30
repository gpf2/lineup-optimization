import random
import numpy as np
from itertools import combinations
import json

num_iterations = 500

def weighted_avg_std(scores):
    weighted_sum = 0
    weights = []
    for i, score in enumerate(reversed(scores)):
        weight = 0.75*(0.25)**i
        weights.append(weight)
        weighted_sum += weight*score

    mean = weighted_sum/np.sum(weights)
    var = 0
    for score, weight in zip(reversed(scores), weights):
        var += weight*(score-mean)**2

    return mean, (var/np.sum(weights))**0.5

#maybe compare past predicted points to past actual scores to see how much to
#weight the past_guess vs the current prediction
#also should try and do some optimization for weights
def simulate_player_score(players, player, week):
    p = players[player]
    
    #if its the first week, only account for the projected points
    if week==1 and len(p["prev season"])==0:
        base = (p["projected points"])[week-1]
        past_guess = None
        projected = base
    #otherwise, combine past performance this season and the projected points
    else:
        mean, std = weighted_avg_std(p["prev season"]+p["scored points"][:week-1])
        #mean = np.mean(p["prev season"]+p["scored points"][:week-1])
        #std = np.std(p["prev season"]+p["scored points"][:week-1])
        #take a random var from a normal distribution of the past performances
        #this season
        past_guess = max(np.random.normal(mean, std), 0)

        #take a combo of the projected points and the past performance
        projected = (p["projected points"])[week-1]
        base = p["weights"][0]*projected + p["weights"][1]*past_guess
    
    prob = random.random()
    #if boom, scale the base up a little
    if prob >= 1-p['boombust'][0]:
        return projected, past_guess, base*random.uniform(p["weights"][2], p["weights"][2]+0.1)
    #if boom, scale the base down a little
    elif prob < p['boombust'][1]:
        return projected, past_guess, base*random.uniform(p["weights"][3]-0.1, p["weights"][3])
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
                proj, guess, score = simulate_player_score(players, p, week)
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

