import numpy as np
import cvxpy as cp
import json


#return 1 hot vector representing which players have a position in positions
def position_vector(positions, players):
    vector = []
    for name in list(players.keys()):
        if players[name]["position"] in positions:
            vector.append(1)
        else:
            vector.append(0)
    return vector

def lp_optimization(players, week):
    assert(len(players)==16)
    names = list(players.keys())
    #x tracks which people we pick like
    #xi between 0 and 1, higher represents we want to pick this player more
    x = cp.Variable(16)

    projected_points = []
    prev_scores = []
    weights = []
    for name in names:
        #get projected points for each player
        player = players[name]
        proj = player["projected points"][week-1]
        projected_points.append(proj)

        #get average past performance for each player
        if week > 1:
            guess = np.mean(player["scored points"][:week-1])
        else:
            guess = 0
        prev_scores.append(guess)
        base = proj*player["weights"][0] + guess*player["weights"][1]
        base = base + 5*(player['boombust'][0]-player['boombust'][1])
        
        #track projected, past, and guess for weight updates
        weights.append(player["weights"][:2])
        player["guessed scores"] = [proj, guess, base]
    projected_points = np.array(projected_points)
    prev_scores = np.array(prev_scores)
    weights = np.array(weights)

    #get vector representing guess of what each player would score this week
    score_vector = weights[:,0]*projected_points + weights[:,1]*prev_scores
    objective = cp.Maximize(score_vector@x)

    constraints = [
        cp.sum(x)==9, #9 total players
        position_vector({"QB"}, players)@x==1,
        position_vector({"RB"}, players)@x>=2, #pick between 2 and 3 rbs
        position_vector({"RB"}, players)@x<=3,
        position_vector({"WR"}, players)@x>=2, #pick between 2 and 3 wrs
        position_vector({"WR"}, players)@x<=3,
        position_vector({"TE"}, players)@x>=1, #pick between 1 and 2 tes
        position_vector({"TE"}, players)@x<=2,
        position_vector({"K"}, players)@x==1,
        position_vector({"DST"}, players)@x==1,
        position_vector({"RB", "WR", "TE"}, players)@x==6, #flex position pick
        x>=0, 
        x<=1,
    ]

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS)

    #get the players that we wanted to pick the most and their team score
    sorted_idxs = np.argsort(-x.value)
    roster = []
    total_score = 0
    for i in sorted_idxs[:9]:
        roster.append(names[i])
        total_score+=score_vector[i]

    return roster, total_score