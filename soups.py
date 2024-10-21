import requests
from bs4 import BeautifulSoup

# Function to scrape the last updated date
def scrape_last_updated_date(url):
    # Send GET request to fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

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

# Example usage:
url = 'https://nbctf.mod.gov.il/he/MinisterSanctions/Announcements/Pages/nbctfDownloads.aspx'
last_updated_date = scrape_last_updated_date(url)
if last_updated_date:
    print(f"Last updated date: {last_updated_date}")
else:
    print("Failed to extract the last updated date.")
