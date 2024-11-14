from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Set up Selenium WebDriver options
options = Options()
options.headless = True  # Run in headless mode (without opening a browser window)

# Initialize WebDriver without specifying a path, assuming WebDriver is in PATH
driver = webdriver.Chrome(options=options)

# Load Twitter links from the CSV file and rename the single column
try:
    twitter_links_df = pd.read_csv(r'E:\twitter Scrape\twitter_links.csv')
    print("CSV file loaded successfully.")
    twitter_links_df.columns = ['Twitter_Link']  # Rename the column
except FileNotFoundError:
    print("The specified CSV file was not found.")
    exit()

# Initialize an empty list to store scraped data
data = []

# Iterate over each Twitter link in the CSV file
for index, row in twitter_links_df.iterrows():
    url = row['Twitter_Link']
    
    # Load the Twitter profile page
    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load fully
        print(f"Accessing {url}")
    except Exception as e:
        print(f"Failed to load page for {url}: {e}")
        # Append N/A values for this row if there is an issue loading the page
        data.append({
            'Bio': 'N/A',
            'Following Count': 'N/A',
            'Followers Count': 'N/A',
            'Location': 'N/A',
            'Website': 'N/A'
        })
        continue

    # Scrape the required data
    try:
        bio = driver.find_element(By.CSS_SELECTOR, "div[data-testid='UserDescription']").text if driver.find_elements(By.CSS_SELECTOR, "div[data-testid='UserDescription']") else 'N/A'
        following_count = driver.find_element(By.XPATH, "//a[contains(@href, '/following')]//span").text if driver.find_elements(By.XPATH, "//a[contains(@href, '/following')]//span") else 'N/A'
        followers_count = driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]//span").text if driver.find_elements(By.XPATH, "//a[contains(@href, '/followers')]//span") else 'N/A'
        location = driver.find_element(By.CSS_SELECTOR, "span[data-testid='UserLocation']").text if driver.find_elements(By.CSS_SELECTOR, "span[data-testid='UserLocation']") else 'N/A'
        website = driver.find_element(By.CSS_SELECTOR, "a[data-testid='UserUrl']").get_attribute('href') if driver.find_elements(By.CSS_SELECTOR, "a[data-testid='UserUrl']") else 'N/A'
        
        # Append scraped data to the list
        data.append({
            'Bio': bio,
            'Following Count': following_count,
            'Followers Count': followers_count,
            'Location': location,
            'Website': website
        })
        print(f"Data scraped successfully for {url}.")
    
    except Exception as e:
        print(f"Error parsing data for {url}: {e}")
        # In case of error during scraping, append N/A values
        data.append({
            'Bio': 'N/A',
            'Following Count': 'N/A',
            'Followers Count': 'N/A',
            'Location': 'N/A',
            'Website': 'N/A'
        })
        continue

# Check if data is collected
print(f"Collected {len(data)} entries.")

# Close the WebDriver
driver.quit()

# Ensure the output file path is correct
output_path = 'twitter_profiles.csv'
print(f"Saving data to {output_path}")

# Convert the data into a DataFrame and save it as a CSV file
if data:
    output_df = pd.DataFrame(data)
    output_df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}.")
else:
    print("No data to save.")
