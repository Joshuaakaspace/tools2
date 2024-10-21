from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import time
import requests

# Step 1: Function to scrape the table and extract the last updated date using Selenium
def scrape_last_updated_date(url):
    # Setup Selenium WebDriver (Make sure you have the appropriate WebDriver for your browser)
    driver = webdriver.Chrome()  # or use webdriver.Firefox(), webdriver.Edge(), etc.
    driver.get(url)
    
    # Wait for the page to load fully
    time.sleep(5)

    # Get the page source and pass it to BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()  # Close the browser after page load

    # Find the div containing the table with the last updated date
    table_div = soup.find('div', {'id': 'ctl00_PlaceHolderMain_ctl02_ctl02__ControlWrapper_RichHtmlField'})
    
    # Ensure we found the correct div
    if not table_div:
        print("Could not find the table div.")
        return None

    # Find the first table (the one containing the last updated date)
    table = table_div.find('table')
    
    if table is None:
        print("Could not find the table inside the div.")
        return None

    # Find all the rows in the table
    rows = table.find_all('tr')

    # Iterate through rows and check if 'XLSX' is mentioned, then extract the date
    for row in rows:
        cols = row.find_all('td')
        # Ensure that there are enough columns and check for 'XLSX' in the first column
        if len(cols) > 1 and "XLSX" in cols[0].text:
            last_updated_date = cols[1].text.strip()
            return last_updated_date

    return None

# Step 2: Function to check if the date is new
def is_date_new(last_updated_date, log_file):
    # Check if log file exists
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            previous_date = file.read().strip()

        # Compare dates
        if previous_date == last_updated_date:
            return False  # Date is the same, no need to download
    return True  # Date is new, proceed with download

# Step 3: Function to log the new date
def log_last_updated_date(last_updated_date, log_file):
    with open(log_file, 'w') as file:
        file.write(last_updated_date)

# Step 4: Function to download the Excel file and save it with date in filename
import requests

# Step 4: Function to download the Excel file using requests with headers
def download_excel_file(download_url, last_updated_date, folder):
    # Ensure the artifacts folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Prepare the filename with date
    filename = f"terror_organization_designation_list_{last_updated_date.replace('.', '-')}.xlsx"
    output_file = os.path.join(folder, filename)

    # Define headers (simulate a real browser request)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Download the file with the proper headers
    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"Excel file downloaded successfully and saved as {output_file}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
    
    return output_file


# Step 5: Function to read the Excel file and set the first row as the header
def read_excel_as_dataframe(excel_file):
    # Load the Excel file with the first row as the header
    df = pd.read_excel(excel_file, header=1)  # Set header to the first row
    return df

# Main workflow
def main():
    # Define URLs and file paths
    table_url = 'https://nbctf.mod.gov.il/he/MinisterSanctions/Announcements/Pages/nbctfDownloads.aspx'
    excel_url = 'https://nbctf.mod.gov.il/he/Announcements/Documents/NBCTFIsrael%20-%20Terror%20Organization%20Designation%20List_XL.xlsx'
    log_file = 'last_updated_log.txt'
    artifacts_folder = 'artifacts'

    # Check if log file exists
    if not os.path.exists(log_file):
        # Scrape the last updated date to download the Excel file with the date
        last_updated_date = scrape_last_updated_date(table_url)
        if last_updated_date:
            excel_file = download_excel_file(excel_url, last_updated_date, artifacts_folder)
            # Read the Excel file as a DataFrame and set the first row as the header
            df = read_excel_as_dataframe(excel_file)
            # Display the DataFrame (assuming ace_tools or similar is available)
            import ace_tools as tools; tools.display_dataframe_to_user(name="Excel Data", dataframe=df)
    else:
        # Scrape the last updated date
        last_updated_date = scrape_last_updated_date(table_url)

        if last_updated_date:
            # Check if the date is new
            if is_date_new(last_updated_date, log_file):
                # Log the new date
                log_last_updated_date(last_updated_date, log_file)

                # Download the Excel file with the new date in the filename
                excel_file = download_excel_file(excel_url, last_updated_date, artifacts_folder)
                # Read the Excel file as a DataFrame and set the first row as the header
                df = read_excel_as_dataframe(excel_file)
                # Display the DataFrame (assuming ace_tools or similar is available)
                import ace_tools as tools; tools.display_dataframe_to_user(name="Excel Data", dataframe=df)
            else:
                print("No new updates. The file is up to date.")
        else:
            print("Could not find the last updated date.")

if __name__ == "__main__":
    main()
