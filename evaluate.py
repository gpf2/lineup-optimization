#given a roster and a week, determine the actual # of fantasy points scored
import json
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

from stochastic_montecarlo import generate_valid_rosters
rosters = generate_valid_rosters(players)

week = 3
roster = ('Baltimore Ravens', 'Dalton Kincaid', 'Breece Hall', 'Jalen Hurts', 'George Pickens', 'Jake Elliott', "De'Von Achane", 'Chris Olave', 'CeeDee Lamb')
total_score = 0
expected_score = 104.26803579598028
for player in roster:
    for p in players:
        if p["name"]==player:
            break
    total_score+=(p["scored points"])[week-1]
print(total_score)

for r in rosters:
    score = 0
    for player in r:
        for p in players:
            if p["name"]==player:
                break
        score+=(p["scored points"])[week-1]
    if score>total_score:
        print(score)
        print(r)