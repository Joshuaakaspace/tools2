import re
import requests
from bs4 import BeautifulSoup

# Function to clean up the text
def clean_text(text):
    # Remove extra whitespace and newlines
    return re.sub(r'\s+', ' ', text).strip()

# Function to extract data from the table
def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    
    all_data = []
    
    for table in tables:
        headers = [clean_text(th.text) for th in table.find_all('th')]
        
        if not headers:
            # If no th elements, use first row as headers
            headers = [clean_text(td.text) for td in table.find('tr').find_all('td')]
        
        rows = table.find_all('tr')[1:]  # Skip the header row
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                entry = {}
                for header, cell in zip(headers, cells):
                    entry[header] = clean_text(cell.text)
                all_data.append(entry)
    
    return all_data

# Function to convert the extracted data to a Markdown table
def data_to_markdown(data):
    if not data:
        return "No data to display."
    
    # Extract headers from the first dictionary entry
    headers = data[0].keys()
    
    # Create Markdown header row
    markdown_str = '| ' + ' | '.join(headers) + ' |\n'
    markdown_str += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    
    # Add each row of data
    for entry in data:
        row = '| ' + ' | '.join(entry.values()) + ' |\n'
        markdown_str += row
    
    return markdown_str

# Fetch HTML content from a URL using requests
url = 'https://example.com/your-table-page'  # Replace with the actual URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    html_content = response.text
    
    # Extract data from the table
    extracted_data = extract_table_data(html_content)
    
    # Convert extracted data to Markdown and print
    markdown_output = data_to_markdown(extracted_data)
    print(markdown_output)
else:
    print(f"Failed to retrieve page, status code: {response.status_code}")
