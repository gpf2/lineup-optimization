'''
writes results to json following like below:
{
    "Player Name": [
        projected pts for week 1, 
        projected pts for week 2,
        ...
    ],
    ...
}

so if Player A has 10.0 points projected for each week it looks like
{
    "Player A": [
        10.0, 10.0, 10.0, ..., 10.0
    ],
    ...
}
'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time

def get_projections(roster):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    points = {player: [] for player in roster}
    players_search = [p.lower() for p in roster]
    players_search = [p.replace(" ", "+") for p in players_search]


    for week in range(1,15):
        print(week)
        for i in range(len(players_search)):
            player = players_search[i]
            try:
                url = f"https://fantasy.nfl.com/research/search?searchQuery={player}&jSubmit=Submit&statCategory=projectedStats&statType=weekProjectedStats&statSeason=2024&statWeek={week}&sort=projectedPts&position=O"
                driver.get(url)
                time.sleep(3)

                row = driver.find_element(By.CSS_SELECTOR, "table.tableType-player tbody tr")
                cols = row.find_elements(By.TAG_NAME, "td")
                name = cols[0].text.strip()
                name = name.split("\n")[0]
                fpts = float(cols[-1].text.strip())
                points[name].append(fpts)
            except:
                points[roster[i]].append(0.0)

    driver.quit()

    with open("points.json", "w") as f:
        json.dump(points, f, indent=4)
players = ["Jalen Hurts", "Tua Tagovailoa", "Christian McCaffrey", "Breece Hall",
           "De'Von Achane", "Isiah Pacheco", "CeeDee Lamb", "Chris Olave",
           "Christian Kirk", "George Pickens", "T.J. Hockenson", "Dalton Kincaid",
           "Baltimore Ravens", "Philadelphia Eagles", "Jake Elliott", "Brandon McManus"]
get_projections(players)

