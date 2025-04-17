import numpy as np
import time
from collections import defaultdict
from helperfunct import generate_lineups, initialize_player_data
from integer_program import optimize_lineup_integer
from linear_programs import optimize_lineup_simplex, optimize_lineup_interior
from linear_evaluate import is_valid_roster

def compare_programs(evals, optimize_lineup_linear):
    res = defaultdict(list)
    options = generate_lineups(evals)

    for i in range(evals):
        players = initialize_player_data(options[i])
        #print(f"running eval {i}")
        for week in range(1, 16):  
            # time lp & make sure roster is valid
            lp_start = time.time()
            lp_roster, lp_proj_score = optimize_lineup_linear(players, week)
            lp_time = time.time() - lp_start
            lp_valid = is_valid_roster(lp_roster) 
            #print(f"lproster: {lp_roster}")
        
            # time ip & make sure roster is valid
            ip_start = time.time()
            ip_roster, ip_proj_score = optimize_lineup_integer(players, week)
            ip_time = time.time() - ip_start
            ip_valid = is_valid_roster(ip_roster)

            # get actual scores for players selected to start in lp & ip
            lp_actual_score = sum(players[p]["scored points"][week - 1] for p in lp_roster)
            ip_actual_score = sum(players[p]["scored points"][week - 1] for p in ip_roster)

            # compare error for prediction between lp & ip IDK if we need
            lp_pred_error = abs(lp_proj_score - lp_actual_score)
            ip_pred_error = abs(ip_proj_score - ip_actual_score)

            res["lp_score"].append(lp_actual_score)
            res["ip_score"].append(ip_actual_score)
            res["score_diff"].append(ip_actual_score - lp_actual_score)
            res["lp_time"].append(lp_time)
            res["ip_time"].append(ip_time)
            res["lp_valid"].append(lp_valid)
            res["ip_valid"].append(ip_valid)
            res["lp_pred_error"].append(lp_pred_error)
            res["ip_pred_error"].append(ip_pred_error)

    #print("hi")
    #print(res["lp_valid"], res["ip_valid"])
    return {
        "avg_lp_score": float(np.mean(res["lp_score"])),
        "avg_ip_score": float(np.mean(res["ip_score"])),
        "score diff": float(np.mean(res["score_diff"])),
        "avg_lp_time": float(np.mean(res["lp_time"])),
        "avg_ip_time": float(np.mean(res["ip_time"])),
        "lp_valid_rate": float(np.sum(res["lp_valid"])/len(res["lp_valid"])), # for some reason when i ran it all of the lps & ips were not valid
        "ip_valid_rate": float(np.sum(res["ip_valid"])/len(res["ip_valid"])),
        "avg_lp_pred_error": float(np.mean(res["lp_pred_error"])),
        "avg_ip_pred_error": float(np.mean(res["ip_pred_error"]))    
    }

print("running for simplex")
print(compare_programs(10, optimize_lineup_simplex))

print("running for interior")
print(compare_programs(10, optimize_lineup_interior))