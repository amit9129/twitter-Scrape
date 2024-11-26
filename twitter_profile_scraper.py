import re
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Validate Twitter URLs
def validate_twitter_url(url):
    twitter_pattern = r'^https://twitter\.com/[A-Za-z0-9_]+$'
    return re.match(twitter_pattern, url)

# Initialize WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run browser in headless mode
    options.add_argument('--no-sandbox')  # Fix for sandbox issues
    options.add_argument('--disable-dev-shm-usage')  # Avoid shared memory issues
    options.add_argument('--disable-gpu')  # Disable GPU rendering
    return webdriver.Chrome(options=options)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('twitter_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS twitter_links (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE,
                        title TEXT,
                        followers_count TEXT)''')
    return conn, cursor

# Scrape Twitter Page Information
def scrape_twitter_data(driver, url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            # Wait for the title
            title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "title"))
            ).get_attribute("innerText")
            
            # Wait for followers count
            followers_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@data-testid, 'UserProfileHeader_Items')]"))
            )
            followers_text = followers_element.text.split("\n")[-1]
            followers_count = followers_text.split(' ')[0]  # Extract number value
            
            return title, followers_count
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(2)  # Small delay before retrying
            if attempt == retries - 1:
                return None, None

# Process and Store Data
def process_links(links, driver, conn, cursor):
    for url in set(filter(validate_twitter_url, links)):
        try:
            # Scrape the data
            title, followers_count = scrape_twitter_data(driver, url)
            if title and followers_count:
                cursor.execute(
                    "INSERT OR IGNORE INTO twitter_links (url, title, followers_count) VALUES (?, ?, ?)",
                    (url, title, followers_count)
                )
                conn.commit()
                print(f"Data stored: {url} | {title} | {followers_count}")
            else:
                print(f"Failed to scrape data for {url}")
        except sqlite3.IntegrityError:
            print(f"Duplicate URL skipped: {url}")
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")

# Main Function
def main():
    # Input list of Twitter URLs
    twitter_urls = [
        "https://twitter.com/GTNUK1",
        "https://twitter.com/whatsapp",
        "https://twitter.com/aacb_CBPTrade",
        "https://twitter.com/aacbdotcom",
        "https://twitter.com/@AAWindowPRODUCT",
        "https://www.twitter.com/aandb_kia",
        "https://twitter.com/ABHomeInc",
        "https://twitter.com/Abrepro",
        "http://www.twitter.com",
        "https://twitter.com/ACChristofiLtd",
        "https://twitter.com/aeclothing1",
        "http://www.twitter.com/",
        "https://twitter.com/AETechnologies1",
        "http://www.twitter.com/wix",
        "https://twitter.com/AGInsuranceLLC"
    ]

    # Remove invalid URLs and duplicates
    valid_urls = list(set(filter(validate_twitter_url, twitter_urls)))

    # Initialize the driver and database
    driver = init_driver()
    conn, cursor = init_db()

    # Process links
    process_links(valid_urls, driver, conn, cursor)

    # Close resources
    driver.quit()
    conn.close()

if __name__ == "__main__":
    main()
