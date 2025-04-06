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

def get_weekly_injuries(week):
    url = f"https://www.fftoday.com/nfl/24_inactives_wk{week}.html"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    inactive_players = []

    for ul in soup.find_all("ul"):
        for li in ul.find_all("li"):
            player_info = li.get_text(strip=True)
            parts = player_info.split()
            name = " ".join(parts[1:])
            inactive_players.append(name)

    return inactive_players

def get_injuries(roster):
    injuries = {player: [] for player in roster}
    for week in range(1, 5):
        print(week)
        injured_players = get_weekly_injuries(week)
        
        for player in roster:
            for injured in injured_players:
                if player in injured:
                    injuries[player].append(week)
                    break
    
    print(injuries)
    with open("injuries.json", "w") as f:
        json.dump(injuries, f, indent=4)

get_injuries(["Taron Johnson"])
