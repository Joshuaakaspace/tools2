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
    
    for table in soup.find_all('table'):
        headers = []
        rows = []
        
        # Attempt to extract headers (using both <th> and first row <td> as fallback)
        header_row = table.find('tr')
        if header_row:
            headers = [header.get_text(strip=True) for header in header_row.find_all(['th', 'td'])]

        # Extract table rows as key-value pairs
        for row in table.find_all('tr')[1:]:
            values = [value.get_text(strip=True) for value in row.find_all('td')]
            if headers and values:
                # If the number of headers doesn't match values, use what's available
                row_data = {headers[i]: values[i] for i in range(min(len(headers), len(values)))}
                tables.append(row_data)
    
    # Prepare final output: Combine paragraphs and tables
    output = "\n\n".join(paragraphs) + "\n\n"
    
    for table in tables:
        for key, value in table.items():
            output += f"{key}: {value}\n"
        output += "\n"  # Add a newline after each table

    return output

# Example usage with a URL
url = 'https://example.com'  # Replace with the actual URL
formatted_output = parse_html_improved(url)
print(formatted_output)
