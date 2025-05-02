import json
import numpy as np
with open('json/real_stochastic_results.json', 'r') as file:
    data = json.load(file)

avg_time = 0
avg_score = 0
avg_est = 0
for i in range(5):
    avg_time += np.mean(data[str(i)]["times"])
    avg_score += np.mean(data[str(i)]["actual"])
    avg_est += np.mean(data[str(i)]["proj"])

print(avg_time/5)
print(avg_score/5)