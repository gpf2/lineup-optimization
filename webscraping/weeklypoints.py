from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def scrape_weekly_scores(year):
    url = f"https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year={year}"
    print(f"Scraping weekly scores from: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5) 
    res = {}

    try:
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if not cols:
                continue

            name = cols[1].text.strip()
            pos = cols[2].text.strip()
            weekly_points = {}

            for week in range(1,18):  
                cell_text = cols[3 + week].text.strip()
                week_number = str(week)

                if cell_text == "BYE" or cell_text == "":
                    weekly_points[week_number] = None
                else:
                    try:
                        weekly_points[week_number] = float(cell_text)
                    except ValueError:
                        weekly_points[week_number] = None

            avg = float(cols[-2].text.strip())
            ttl = float(cols[-1].text.strip())

            res[name] = {
                "Position": pos,
                "Year": year,
                "WeeklyPoints": weekly_points,
                "AVG": avg,
                "TTL": ttl
            }
    except Exception as e:
        print(f"Failed to scrape: {e}")
    driver.quit()
    return res

# data = scrape_weekly_scores(2024)

# with open("weekly_fantasy_scores_2024.json", "w") as f:
#     json.dump(data, f, indent=4)
