import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Step 1: Function to log messages to a log file
def log_message(message, log_file="process_log.txt"):
    with open(log_file, 'a') as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Step 2: Function to scrape the table and extract the last updated date using Selenium
def scrape_last_updated_date(url, log_file="process_log.txt"):
    # Setup Selenium WebDriver in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    log_message("Starting Selenium to scrape the last updated date...", log_file)

    driver.get(url)
    time.sleep(5)  # Wait for the page to load fully

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    log_message("Selenium session completed. Extracting last updated date...", log_file)

    table_div = soup.find('div', {'id': 'ctl00_PlaceHolderMain_ctl02_ctl02__ControlWrapper_RichHtmlField'})
    if not table_div:
        log_message("Could not find the table div.", log_file)
        return None

    table = table_div.find('table')
    if table is None:
        log_message("Could not find the table inside the div.", log_file)
        return None

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1 and "XLSX" in cols[0].text:
            last_updated_date = cols[1].text.strip()
            log_message(f"Found last updated date: {last_updated_date}", log_file)
            return last_updated_date

    log_message("Failed to find the last updated date.", log_file)
    return None

# Step 3: Function to check if the date is new
def is_date_new(last_updated_date, log_file_path, log_file="process_log.txt"):
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            previous_date = file.read().strip()
        if previous_date == last_updated_date:
            log_message("No new updates. The last updated date is the same.", log_file)
            return False
    return True

# Step 4: Function to log the new date
def log_last_updated_date(last_updated_date, log_file_path, log_file="process_log.txt"):
    with open(log_file_path, 'w') as file:
        file.write(last_updated_date)
    log_message(f"Logged new last updated date: {last_updated_date}", log_file)

# Step 5: Function to download the Excel file using Selenium and rename it to IMOD_LIST with date
def download_and_rename_excel_file(download_url, last_updated_date, folder, log_file="process_log.txt"):
    # Ensure the artifacts folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Configure Chrome options to set the download folder in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(folder),  # Set the download directory
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)
    log_message(f"Starting Selenium to download the file: {download_url}", log_file)

    driver.get(download_url)
    time.sleep(10)  # Wait for the file to download

    driver.quit()
    log_message(f"File downloaded successfully to {folder}", log_file)

    original_filename = "NBCTFIsrael - Terror Organization Designation List_XL.xlsx"
    new_filename = f"IMOD_LIST_{last_updated_date.replace('.', '-')}.xlsx"
    
    original_file_path = os.path.join(folder, original_filename)
    new_file_path = os.path.join(folder, new_filename)

    if os.path.exists(original_file_path):
        shutil.move(original_file_path, new_file_path)  # Rename the file
        log_message(f"File renamed to {new_file_path}", log_file)
    else:
        log_message(f"Original file not found: {original_file_path}", log_file)

# Main workflow
def main():
    # Define URLs and file paths
    table_url = 'https://nbctf.mod.gov.il/he/MinisterSanctions/Announcements/Pages/nbctfDownloads.aspx'
    excel_url = 'https://nbctf.mod.gov.il/he/Announcements/Documents/NBCTFIsrael%20-%20Terror%20Organization%20Designation%20List_XL.xlsx'
    log_file_path = 'last_updated_log.txt'
    artifacts_folder = 'artifacts'
    process_log_file = 'process_log.txt'

    # Check if log file exists
    if not os.path.exists(log_file_path):
        # Scrape the last updated date to download the Excel file with the date
        last_updated_date = scrape_last_updated_date(table_url, process_log_file)
        if last_updated_date:
            download_and_rename_excel_file(excel_url, last_updated_date, artifacts_folder, process_log_file)
            # Log the new date
            log_last_updated_date(last_updated_date, log_file_path, process_log_file)
    else:
        # Scrape the last updated date
        last_updated_date = scrape_last_updated_date(table_url, process_log_file)

        if last_updated_date:
            # Check if the date is new
            if is_date_new(last_updated_date, log_file_path, process_log_file):
                # Log the new date
                log_last_updated_date(last_updated_date, log_file_path, process_log_file)

                # Download the Excel file and rename it to IMOD_LIST_<last_updated_date>.xlsx
                download_and_rename_excel_file(excel_url, last_updated_date, artifacts_folder, process_log_file)
            else:
                log_message("No new updates. The file is up to date.", process_log_file)
        else:
            log_message("Could not find the last updated date.", process_log_file)

if __name__ == "__main__":
    main()
