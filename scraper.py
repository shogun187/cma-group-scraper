import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def setup_driver():
    # Set up the Selenium WebDriver (assume chromedriver is in PATH)
    service = Service("F:/projects/chromedriver.exe")  # Change to the path where chromedriver is located
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless Chrome
    options.add_argument("start-maximized")

    # Set page load strategy
    options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(service=service, options=options)

    print("WebDriver Created")

    driver.delete_all_cookies()

    print("Cookies deleted")

    return driver


def scrape_vessel_data(url, driver):
    driver.get(url)

    time.sleep(1)

    # Get the page source and parse with BeautifulSoup
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')

    return scrape_fields(soup)

def scrape_fields(soup):
    data = {}

    # ----- SCRAPE "General Information" TABLE -----
    # Find the <h3> with text "General Information" and then the following table
    gen_info_header = soup.find("h3", text="General Information")
    if gen_info_header:
        gen_info_table = gen_info_header.find_next("table", class_="boat-detail")
        if gen_info_table:
            rows = gen_info_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    data[key] = value

    # ----- SCRAPE "Technical Information" TABLE -----
    tech_info_header = soup.find("h3", text="Technical Information")
    if tech_info_header:
        tech_info_table = tech_info_header.find_next("table", class_="boat-detail")
        if tech_info_table:
            rows = tech_info_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    data[key] = value

    return data

def main(input_excel, output_excel, failed_urls_csv):
    url_df = pd.read_excel(input_excel)

    # Initialize the WebDriver
    driver = setup_driver()

    all_vessel_data = []
    index = 0
    failed_urls = []

    for url in url_df['links']:  # Assuming the column containing URLs is named 'links'
        index += 1
        start_time = time.time()  # Record the start time
        try:
            print(f"{index}. Scraping data for {url}")

            vessel_data = scrape_vessel_data(url, driver)
            all_vessel_data.append(vessel_data)


        except Exception as e:
            print(f"Failed due to {e}")
            failed_urls.append(url)
            continue

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Done in {time_taken:.2f}s")

    print("______________________")
    print("______________________")
    print("______________________")
    print("Retrying failed urls")
    print("______________________")
    print("______________________")
    print("______________________")
    print("______________________")


    index = 0

    for failed_url in failed_urls:

        index += 1
        start_time = time.time()  # Record the start time
        try:
            print(f"{index}. Scraping data for failed url {url}")

            vessel_data = scrape_vessel_data(url, driver)
            all_vessel_data.append(vessel_data)


        except Exception as e:
            print(f"Failed due to {e}")
            continue

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Done in {time_taken:.2f}s")
        failed_urls.remove(failed_url)

    # Close the driver
    driver.quit()

    # Create a DataFrame from the list of dictionaries
    combined_df = pd.DataFrame(all_vessel_data)

    # Save the combined DataFrame to an Excel file
    combined_df.to_excel(output_excel, index=False)

    print(f"Vessel data has been saved to {output_excel}")


    # Save the failed URLs to a CSV file
    failed_urls_df = pd.DataFrame(failed_urls, columns=['failed_url'])
    failed_urls_df.to_csv(failed_urls_csv, index=False)
    print(f"Failed URLs have been saved to {failed_urls_csv}")

if __name__ == "__main__":
    input_excel = 'CC1224.xlsx'  # Path to the input Excel file containing URLs
    output_excel = 'combined_vessel_data.xlsx'  # Path to the output Excel file
    failed_urls_csv = 'failed_urls.csv'
    main(input_excel, output_excel, failed_urls_csv)

    # BEST TO CLEAR CHROME BROWSER CACHE BEFORE RUNNING