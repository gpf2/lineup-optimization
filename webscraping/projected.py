from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import json

projected_points = {}
'''
for week in range(1, 19):
    print(week)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = f"https://fantasy.nfl.com/research/players?position=O&statCategory=stats&statSeason=2024&statType=weekStats&statWeek={week}&sort=pts"
    driver.get(url)

    time.sleep(3)

    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, 'table.tableType-player tbody tr')

        for row in rows:
            try:
                name = row.find_element(By.CSS_SELECTOR, 'a.playerNameFull').text.strip()
                points = row.find_elements(By.CSS_SELECTOR, 'td')[-1].text.strip()
                if name and points:
                    if week==1:
                        projected_points[name] = [float(points)]
                    else:
                        projected_points[name].append(float(points))
            except Exception:
                continue

        try:
            next_button = driver.find_element(By.LINK_TEXT, '>')
            if 'disabled' in next_button.get_attribute('class'):
                break
            next_button.click()
            time.sleep(2)
        except:
            break

    driver.quit()
'''
rosters = ['Brandon Aubrey', 'Chris Boswell', 'Cameron Dicker', "Ka'imi Fairbairn", 'Jason Sanders', 'Chase McLaughlin', 'Jake Bates', 'Wil Lutz', 'Tyler Bass', 'Daniel Carlson', 'Justin Tucker', 'Jake Elliott', 'Jason Myers', 'Matt Gay', 'Joshua Karty', 'Blake Grupe', 'Will Reichard', 'Cam Little', 'Chad Ryland', 'Younghoe Koo', 'Joey Slye', 'Jake Moody', 'Austin Seibert', 'Cairo Santos', 'Nick Folk', 'Eddy Pineiro', 'Harrison Butker', 'Brandon McManus', 'Evan McPherson', 'Dustin Hopkins', 'Greg Joseph', 'Anders Carlson', 'Brayden Narveson', 'Matthew Wright', 'Graham Gano', 'Parker Romo', 'Cade York', 'Greg Zuerlein', 'Zane Gonzalez', 'Matt Prater', 'Riley Patterson', 'Spencer Shrader', 'Jude McAtamney', 'Jack Browning']
def scrape_all_rosters():
    url = "https://www.nfl.com/sitemap/html/rosters/2024/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select("ul li a")

    urls = {}
    for link in links:
        urls[link.text.strip()] = "https://www.nfl.com" + link['href']

    for team_name, team_url in urls.items():
        rosters.append(team_name)
        print(team_name)
        time.sleep(1)
#scrape_all_rosters()

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
rosters_search = [r.lower() for r in rosters]
rosters_search = [r.replace(" ", "+") for r in rosters_search]

for week in range(1,19):
    print(week)
    for i in range(len(rosters_search)):
        if week==1:
            projected_points[rosters[i]]=[]
        player = rosters_search[i]
        try:
            url = f"https://fantasy.nfl.com/research/search?searchQuery={player}&jSubmit=Submit&statCategory=projectedStats&statType=weekProjectedStats&statSeason=2024&statWeek={week}&sort=projectedPts&position=O"
            driver.get(url)
            time.sleep(3)

            row = driver.find_element(By.CSS_SELECTOR, "table.tableType-player tbody tr")
            cols = row.find_elements(By.TAG_NAME, "td")
            name = cols[0].text.strip()
            name = name.split("\n")[0]
            fpts = float(cols[-1].text.strip())
            projected_points[rosters[i]].append(fpts)
        except:
            projected_points[rosters[i]].append(0.0)

driver.quit()

with open("kicker_points.json", "w") as f:
    json.dump(projected_points, f, indent=4)