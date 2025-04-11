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
    players[p]["weights"] = [0.5, 0.5, 1.1, 0.9]
    players[p]["guessed scores"] = [0, 0, 0]