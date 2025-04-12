import json
import random

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
