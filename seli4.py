import os
import pandas as pd
from datetime import datetime
from tools.imod_scraper import scrape_last_updated_date, is_date_new, download_and_rename_excel_file
from tools.imod_delta import process_differences, compare_files
import logging

# Setup logging for Airflow tasks
def log_message(message, log_file="process_log.log"):
    with open(log_file, 'a') as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Task 1: Download the IMOD data
def imod_source_download(**kwargs):
    # Initialize variables
    table_url = 'https://nbctf.mod.gov.il/he/MinisterSanctions/Announcements/Pages/nbctfDownloads.aspx'
    excel_url = 'https://nbctf.mod.gov.il/he/Announcements/Documents/NBCTF%20Israel%20designation%20of%20Individuals%20XL.xlsx'
    log_file_path = 'last_updated_log.txt'
    artifacts_folder = 'Artifacts'
    process_log_file = 'process_log.log'

    # Scrape last updated date
    last_updated_date = scrape_last_updated_date(table_url, log_file_path)
    if last_updated_date:
        # Check if there's a new date
        if is_date_new(last_updated_date, log_file_path, process_log_file):
            file_path = download_and_rename_excel_file(excel_url, last_updated_date, artifacts_folder, process_log_file)
            if file_path:
                log_message(f"Downloaded and saved file to {file_path}", process_log_file)
                
                # Convert Excel to JSON
                df = pd.read_excel(file_path)
                json_data_new = df.to_json(orient='records')
                
                # Save the new JSON to XCom
                ti = kwargs['ti']
                ti.xcom_push(key='jsonDataNew', value=json_data_new)
                
                # Optionally pull old JSON data from somewhere (e.g., S3 or previous download)
                old_json_data = fetch_old_data()
                ti.xcom_push(key='jsonDataOld', value=old_json_data)

            else:
                log_message(f"No updates. The file is up to date.", process_log_file)
        else:
            log_message("Could not find the last updated date.", process_log_file)

# Task 2: Detect differences (delta)
def imod_delta_detection(**kwargs):
    ti = kwargs['ti']
    
    # Pull old and new data from XCom
    old_json_data = ti.xcom_pull(task_ids='IMOD-source-download', key='jsonDataOld')
    new_json_data = ti.xcom_pull(task_ids='IMOD-source-download', key='jsonDataNew')

    if old_json_data and new_json_data:
        # Compare the files and detect delta
        delta = process_differences(old_json_data, new_json_data)
        
        # Save delta result to file (optional)
        delta_file_path = os.path.join('Artifacts', 'delta.json')
        with open(delta_file_path, 'w') as delta_file:
            delta_file.write(delta)
        
        # Push delta result to XCom if needed for further tasks
        ti.xcom_push(key='deltaResult', value=delta)
        
        log_message(f"Delta detected and saved to {delta_file_path}", "process_log.log")
    else:
        log_message("Missing data for delta detection", "process_log.log")

def fetch_old_data():
    # Placeholder function for retrieving old data (e.g., from S3 or previous download)
    old_data = []  # Retrieve old data logic goes here
    return old_data

if __name__ == "__main__":
    main()
