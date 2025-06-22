import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os

# --- CONFIGURATION ---
OUTPUT_CSV = "data/outdoorsy.csv"
SEARCH_URL = "https://www.outdoorsy.com/rv-rentals/los-angeles--ca?pickupDate=2025-08-25&dropoffDate=2025-09-02&delivery=false"
HEADLESS = True
RESULTS_LIMIT = 50

# --- SETUP SELENIUM OPTIONS ---
options = Options()
if HEADLESS:
    options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# --- HELPER FUNCTIONS ---
def safe_find(element, selector, by=By.CSS_SELECTOR):
    try:
        return element.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return ""

def scrape_outdoorsy():
    print("Starting Outdoorsy scraper...")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    listings = []

    try:
        driver.get(SEARCH_URL)
        time.sleep(5)

        cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="listing-card-wrapper"]')
        print(f"Found {len(cards)} listings.")

        for i, card in enumerate(cards):
            if i >= RESULTS_LIMIT:
                break

            try:
                title = safe_find(card, '[data-testid="listing-title"]')
                price = safe_find(card, '[data-testid="price"]')
                location = safe_find(card, '[data-testid="listing-location"]')
                desc = safe_find(card, '[data-testid="listing-description"]')
                url = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                burning_man_allowed = "burning man" in (title + desc).lower()

                listings.append({
                    "Name": title,
                    "Price per night": price,
                    "Pickup City": location,
                    "Description": desc,
                    "URL": url,
                    "Burning Man Allowed": "Yes" if burning_man_allowed else "Unknown",
                    "Platform": "Outdoorsy"
                })

            except Exception as e:
                print(f"Error on card {i}: {e}")
                continue

    except TimeoutException:
        print("Page load timeout.")
    finally:
        driver.quit()

    df = pd.DataFrame(listings)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Outdoorsy data saved to {OUTPUT_CSV} ({len(df)} records).")

if __name__ == "__main__":
    scrape_outdoorsy()