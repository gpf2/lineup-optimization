'''
writes results to json following like below:
{
    "Player Name": [
        week they were injured,
        next week they were injured, ...
    ],
    ...
}

so if Player A is injured for weeks 2,5,6 it looks like
{
    "Player A": [
        2, 5, 6
    ],
    ...
}
'''

import requests
from bs4 import BeautifulSoup
import json

players = [
    "Patrick Mahomes", "Tyreek Hill", "Christian McCaffrey", "Nick Bolton",
]

injuries = {player: [] for player in players}

def get_weekly_injuries(week_num):
    url = f"https://www.nfl.com/injuries/league/2024/reg{week_num}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')

    tables = soup.find_all("table")

    injured_players = set()
    for table in tables:
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if columns:
                name = columns[0].get_text(strip=True)
                injured_players.add(name.lower())
    return injured_players

for week in range(1, 15):
    print(week)
    injured_players = get_weekly_injuries(week)
    
    for player in players:
        if player.lower() in injured_players:
            injuries[player].append(week)

with open("injuries.json", "w") as f:
    json.dump(injuries, f, indent=4)