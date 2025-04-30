import json
import numpy as np
with open('stochastic_results.json', 'r') as file:
    data = json.load(file)

avg_time = 0
avg_score = 0
avg_est = 0
for i in range(25):
    avg_time += np.mean(data[str(i)]["times"])
    avg_score += np.mean(data[str(i)]["actual"])
    avg_est += np.mean(data[str(i)]["proj"])

print(avg_time/25)
print(avg_score/25)
print(avg_est/25)