from linear_programs import *
from integer_program import *
from stochastic_montecarlo import generate_valid_rosters
from helperfunct import generate_lineups, initialize_player_data
import json
same = 0
better = 0
#checks if a returned roster is actually valid
def is_valid_roster(roster,players):
    positions = ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'K', 'DST', 'FLEX']
    for player in roster:
        try:
            curr_pos = players[player]["position"]
            if curr_pos in positions:
                positions.remove(curr_pos)
            elif curr_pos not in positions and curr_pos in {'RB', 'WR', 'TE'}:
                positions.remove('FLEX')
            else:
                return False
        except:
            return False
    
    return len(positions)==0

with open('json/generated_lineups.json', 'r') as file:
        options = json.load(file)
num_evals = len(options)
'''
options = generate_lineups(num_evals)
for op in options:
    assert(len(op)==16)
'''
for i in range(num_evals):
    players = initialize_player_data(options[i])
    rosters = generate_valid_rosters(players)
    num_better = 0
    beat_proj = 0
    same_proj = 0
    for week in range(1, 15):
        #get lp roster
        roster, expected_score = optimize_lineup_integer(players, week)
        #print(is_valid_roster(roster,players))
        #print("Guessed score: ", expected_score)

        #compare actual scored points vs what lp guessed
        total_score = 0
        for player in roster:
            total_score+=(players[player]["scored points"])[week-1]
        print("Actual score:", total_score)

        count=0
        better_scores = []
        best_projected_roster = None
        best_projected_score = -np.inf
        for r in rosters:
            score = 0
            proj_score = 0
            #track the total projected points and scored points for a roster
            for player in r:
                score+=(players[player]["scored points"])[week-1]
                proj_score+=(players[player]["projected points"])[week-1]
            #track all rosters that scored higher than monte carlo roster
            if score>total_score:
                better_scores.append(score)
                count+=1
            #track the best roster based on projected points
            if proj_score>best_projected_score:
                best_projected_roster=r
                best_projected_score=proj_score
        #print()
        #print(f"{count} possible rosters had a higher score")
        #if count>0:
        #    print(f"Average better score: {np.mean(better_scores)}")
        #    print(f"Best score: {np.max(better_scores)}")
        #determine what score i would've gotten if picking roster based on
        #projected points
        projected_roster_score = 0
        for player in best_projected_roster:
            projected_roster_score+=(players[player]["scored points"])[week-1]
        print(f"Projected Roster scored {projected_roster_score}")
        print()

        if projected_roster_score<total_score:
            beat_proj+=1
        if projected_roster_score==total_score:
            same_proj+=1
        num_better+=count
        
        #update weights
        if week>1:
            for player in roster:
                proj, guess, score = players[player]["guessed scores"]

                #update weights for guess vs projected points
                actual_score = (players[player]["scored points"])[week-1]
                if abs(proj-actual_score) > abs(guess - actual_score):
                    players[player]["weights"][0]-=0.1
                    players[player]["weights"][1]+=0.1
                else:
                    players[player]["weights"][1]-=0.1
                    players[player]["weights"][0]+=0.1
        players[player]["guessed scores"] = [0, 0, 0]
    if is_valid_roster(roster,players):
        same+=same_proj
        better+=beat_proj
    else:
        print(1)
# print(same/num_evals)
# print(better/num_evals)
