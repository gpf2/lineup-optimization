#given a roster and a week, determine the actual # of fantasy points scored

from stochastic_montecarlo import *
from allie_rostergen import *

same = 0
better = 0
num_evals = 100
options = generate_lineups(num_evals)
for i in range(num_evals):
    num_better = 0
    same_proj = 0
    beat_proj = 0
    players = initialize_player_data(options[i])
    for week in range(1, 15):
        #get monte carlo roster
        roster, expected_score, rosters = monte_carlo_optimization(players, week)
        #print("Guessed score: ", expected_score)

        #compare actual scored points vs what monte carlo guessed
        total_score = 0
        for player in roster:
            total_score+=(players[player]["scored points"])[week-1]
        #print("Actual score:", total_score)

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
        '''
        print()
        print(f"{count} possible rosters had a higher score")
        if count>0:
            print(f"Average better score: {np.mean(better_scores)}")
            print(f"Best score: {np.max(better_scores)}")
        '''
        #determine what score i would've gotten if picking roster based on
        #projected points
        projected_roster_score = 0
        for player in best_projected_roster:
            projected_roster_score+=(players[player]["scored points"])[week-1]
        '''
        print(f"Projected Roster scored {projected_roster_score}")
        print()
        '''
        if projected_roster_score<total_score:
            beat_proj+=1
        if projected_roster_score==total_score:
            same_proj+=1
        num_better+=count
        
        #update weights
        if week>1:
            for player in roster:
                proj, guess, score = players[player]["guessed scores"]
                proj = proj/(len(rosters)*num_iterations)
                guess = guess/(len(rosters)*num_iterations)

                #update weights for guess vs projected points
                actual_score = (players[player]["scored points"])[week-1]
                if abs(proj-actual_score) > abs(guess - actual_score):
                    players[player]["weights"][0]-=0.05
                    players[player]["weights"][1]+=0.05
                else:
                    players[player]["weights"][1]-=0.05
                    players[player]["weights"][0]+=0.05

                #updated weights for boom bust
                if actual_score > proj and proj>0:
                    ratio = actual_score/proj
                    ratio = ratio/10
                    players[player]["weights"][2]+=ratio
                elif actual_score < proj and proj>0:
                    ratio = actual_score/proj
                    ratio = ratio/10
                    players[player]["weights"][3]-=ratio
        players[player]["guessed scores"] = [0, 0, 0]
    '''
    print(f"*****************************************************************")
    print(f"Average # of Higher Teams: {num_better/14}")
    print(f"Beat Projected {beat_proj} times - Same Projected {same_proj} times")
    print(f"*****************************************************************")
    '''
    same += same_proj
    better += beat_proj

print(same/num_iterations)
print(better/num_iterations)