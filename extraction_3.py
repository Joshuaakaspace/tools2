import requests
from lxml import html

def parse_html_lxml_from_url(url):
    # Fetch the content from the URL
    response = requests.get(url, verify=False)
    
    # Parse the HTML content with lxml
    tree = html.fromstring(response.text)
    
    # Extract paragraphs
    paragraphs = tree.xpath('//p')
    extracted_paragraphs = []
    for p in paragraphs:
        # Ensure newline after full stops
        paragraph_text = p.text_content().strip().replace('. ', '.\n')
        extracted_paragraphs.append(paragraph_text)

    # Extract tables
    tables = tree.xpath('//table')
    extracted_tables = []
    for table in tables:
        headers = table.xpath('.//tr[1]/th/text()') or table.xpath('.//tr[1]/td/text()')
        rows = table.xpath('.//tr[position() > 1]')
        for row in rows:
            values = [value.strip() for value in row.xpath('./td/text()')]
            if headers and values:
                row_data = {headers[i]: values[i] for i in range(len(headers))}
                extracted_tables.append(row_data)

    # Prepare final output
    output = "\n\n".join(extracted_paragraphs) + "\n\n"
    for table in extracted_tables:
        for key, value in table.items():
            output += f"{key}: {value}\n"
        output += "\n"

    return output

# Example usage with a URL
url = 'https://example.com'  # Replace with the actual URL you want to scrape
formatted_output = parse_html_lxml_from_url(url)
print(formatted_output)
