from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import time

def scrape_boom_bust_report(year):
    positions = ["QB", "RB", "WR", "TE"]
    base_url = "https://www.fantasypros.com/nfl/reports/boom-bust-{}.php?year={}"
    res = {}
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for pos in positions:
        url = base_url.format(pos.lower(), year)
        print(f"Scraping {pos} data for {year}...")
        driver.get(url)
        time.sleep(5)

        try:
            table = driver.find_element(By.ID, "boom-bust")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:] 

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if not cols:
                    continue
                full_name = cols[1].text.strip()
                name = full_name.split("(")[0].strip()
                games = int(cols[2].text.strip())
                boom = float(cols[3].text.strip().strip('%')) / 100
                top6 = float(cols[4].text.strip().strip('%')) / 100
                top12 = float(cols[5].text.strip().strip('%')) / 100
                bust = float(cols[6].text.strip().strip('%')) / 100
                other = float(cols[7].text.strip().strip('%')) / 100
                consistency = round(1 - bust, 4)

                if name not in res:
                    res[name] = {
                        "Position": pos
                    }
                res[name][str(year)] = {
                    "Games": games,
                    "Boom": boom,
                    "Top 6": top6,
                    "Top 12": top12,
                    "Bust": bust,
                    "Other": other,
                    "Consistency": consistency
                }
        except Exception as e:
            print(f"Failed to scrape {pos}: {e}")
    driver.quit()
    return res

data = scrape_boom_bust_report(2024)
with open("boom_bust_2024.json", "w") as f:
    json.dump(data, f, indent=4)