import os
import shutil
import pandas as pd
from deepdiff import DeepDiff
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Function to log messages to a log file
def log_message(message, log_file="process_log.txt"):
    with open(log_file, 'a') as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Function to scrape the table and extract the last updated date using Selenium
def scrape_last_updated_date(url, log_file="process_log.txt"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    log_message("Starting Selenium to scrape the last updated date...", log_file)

    driver.get(url)
    time.sleep(5)

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

# Function to check if the date is new
def is_date_new(last_updated_date, log_file_path, log_file="process_log.txt"):
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            previous_date = file.read().strip()
        if previous_date == last_updated_date:
            log_message("No new updates. The last updated date is the same.", log_file)
            return False
    return True

# Function to log the new date
def log_last_updated_date(last_updated_date, log_file_path, log_file="process_log.txt"):
    with open(log_file_path, 'w') as file:
        file.write(last_updated_date)
    log_message(f"Logged new last updated date: {last_updated_date}", log_file)

# Function to download the Excel file using Selenium and rename it to IMOD_LIST with date
def download_and_rename_excel_file(download_url, last_updated_date, folder, log_file="process_log.txt"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(folder),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)
    log_message(f"Starting Selenium to download the file: {download_url}", log_file)

    driver.get(download_url)
    time.sleep(10)

    driver.quit()
    log_message(f"File downloaded successfully to {folder}", log_file)

    original_filename = "NBCTFIsrael - Terror Organization Designation List_XL.xlsx"
    new_filename = f"IMOD_LIST_{last_updated_date.replace('.', '-')}.xlsx"
    
    original_file_path = os.path.join(folder, original_filename)
    new_file_path = os.path.join(folder, new_filename)

    if os.path.exists(original_file_path):
        shutil.move(original_file_path, new_file_path)
        log_message(f"File renamed to {new_file_path}", log_file)
        return new_file_path
    else:
        log_message(f"Original file not found: {original_file_path}", log_file)
        return None

# Function to read an Excel file as a dataframe and set the first row as header
def read_excel_as_dataframe(excel_file, log_file="process_log.txt"):
    try:
        df = pd.read_excel(excel_file, header=0)  # First row as header
        log_message(f"Excel file {excel_file} read successfully with the first row as header.", log_file)
        return df
    except Exception as e:
        log_message(f"Error reading Excel file {excel_file}: {str(e)}", log_file)
        return None

# Function to extract DeepDiff formatted output similar to the image format
def process_differences(diff, original_records, updated_records):
    output = []

    if 'iterable_item_added' in diff:
        for path, added_item in diff['iterable_item_added'].items():
            id_value = added_item.get('_unique_id')
            if id_value:
                output.append({
                    'id': id_value,
                    'action_type': 'ADDED',
                    'details': added_item
                })

    if 'iterable_item_removed' in diff:
        for path, removed_item in diff['iterable_item_removed'].items():
            id_value = removed_item.get('_unique_id')
            if id_value:
                output.append({
                    'id': id_value,
                    'action_type': 'REMOVED',
                    'details': removed_item
                })

    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            changed_item = diff['values_changed'][path]
            id_value = changed_item.get('_unique_id')
            if id_value:
                details_before = change['old_value']
                details_after = change['new_value']
                output.append({
                    'id': id_value,
                    'action_type': 'UPDATED',
                    'details': {
                        'before': details_before,
                        'after': details_after
                    }
                })

    return output

# Function to compare the two files and extract differences
def compare_files(file1, file2, output_file, log_file="process_log.txt"):
    original_records = read_excel_as_dataframe(file1, log_file).to_dict(orient='records')
    updated_records = read_excel_as_dataframe(file2, log_file).to_dict(orient='records')

    if original_records and updated_records:
        diff = DeepDiff(original_records, updated_records, ignore_order=True).to_dict()
        formatted_diff = process_differences(diff, original_records, updated_records)

        with open(output_file, 'w') as f:
            f.write(str(formatted_diff))  # Save formatted DeepDiff output
        log_message(f"DeepDiff saved to {output_file}", log_file)
    else:
        log_message("One or both files could not be read for comparison.", log_file)

# Main workflow
def main():
    table_url = 'https://nbctf.mod.gov.il/he/MinisterSanctions/Announcements/Pages/nbctfDownloads.aspx'
    excel_url = 'https://nbctf.mod.gov.il/he/Announcements/Documents/NBCTFIsrael%20-%20Terror%20Organization%20Designation%20List_XL.xlsx'
    log_file_path = 'last_updated_log.txt'
    artifacts_folder = 'artifacts'
    process_log_file = 'process_log.txt'

    last_updated_date = scrape_last_updated_date(table_url, process_log_file)
    if last_updated_date:
        if is_date_new(last_updated_date, log_file_path, process_log_file):
            file_path = download_and_rename_excel_file(excel_url, last_updated_date, artifacts_folder, process_log_file)
            if file_path:
                log_last_updated_date(last_updated_date, log_file_path, process_log_file)

                # Get list of downloaded files to calculate DeepDiff between the last two
                files = sorted([f for f in os.listdir(artifacts_folder) if f.startswith("IMOD_LIST")], reverse=True)
                if len(files) >= 2:
                    file1 = os.path.join(artifacts_folder, files[1])
                    file2 = os.path.join(artifacts_folder, files[0])
                    compare_files(file1, file2, 'deepdiff_result.txt', process_log_file)
                else:
                    log_message("Not enough files for comparison.", process_log_file)
        else:
            log_message("No new updates. The file is up to date.", process_log_file)
    else:
        log_message("Could not find the last updated date.", process_log_file)

if __name__ == "__main__":
    main()
