import requests
from bs4 import BeautifulSoup

def parse_html_improved(url):
    # Fetch the content from the URL
    response = requests.get(url, verify=False)
    
    # Initialize BeautifulSoup object to parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract and format paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        # Clean up paragraph text and add newlines after full stops
        paragraph_text = p.get_text(separator=' ', strip=True).replace('. ', '.\n')
        if paragraph_text:  # Ensure we don't add empty paragraphs
            paragraphs.append(paragraph_text)
    
    # Extract and format tables
    tables = []
    unformatted_rows = []

    for table in soup.find_all('table'):
        headers = []
        rows = []
        
        # Attempt to extract headers (using both <th> and first row <td> as fallback)
        header_row = table.find('tr')
        if header_row:
            headers = [header.get_text(strip=True) for header in header_row.find_all(['th', 'td'])]

        # Extract table rows
        for row in table.find_all('tr')[1:]:
            values = [value.get_text(strip=True) for value in row.find_all('td')]
            
            if len(headers) == len(values):
                # If the number of headers matches the number of values, pair them
                row_data = {headers[i]: values[i] for i in range(len(headers))}
                tables.append(row_data)
            else:
                # If there's a mismatch, just append the values as a list
                unformatted_rows.append(values)
    
    # Prepare final output: Combine paragraphs and tables
    output = "\n\n".join(paragraphs) + "\n\n"
    
    # Add formatted tables with headers
    for table in tables:
        for key, value in table.items():
            output += f"{key}: {value}\n"
        output += "\n"  # Add a newline after each table

    # Add unformatted rows without headers
    if unformatted_rows:
        output += "Unformatted Table Rows:\n"
        for row in unformatted_rows:
            output += f"{', '.join(row)}\n"
    
    return output

# Example usage with a URL
url = 'https://example.com'  # Replace with the actual URL
formatted_output = parse_html_improved(url)
print(formatted_output)
