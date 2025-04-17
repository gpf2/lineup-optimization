import numpy as np
import cvxpy as cp
from helperfunct import position_vector, make_score_vector

def optimize_lineup_integer(players, week):
    names = list(players.keys())
    #x tracks which people we pick like
    #xi between 0 and 1, higher represents we want to pick this player more
    x = cp.Variable(16, boolean=True)
    score_vector = make_score_vector(players,week)
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
    ]

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.GUROBI)

    #get the players that we picked and their team score
    sorted_idxs = np.argsort(-x.value)
    roster = []
    total_score = 0
    for i in sorted_idxs[:9]:
        roster.append(names[i])
        total_score+=score_vector[i]

    return roster, total_score
