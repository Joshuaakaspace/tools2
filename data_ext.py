import re
from bs4 import BeautifulSoup

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def add_newlines(text):
    text = re.sub(r'([.!?])\s+', r'\1\n\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def extract_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    all_data = []

    # Extract table data
    tables = soup.find_all('table')
    for table in tables:
        headers = [clean_text(th.text) for th in table.find_all('th')]
        if not headers:
            headers = [clean_text(td.text) for td in table.find('tr').find_all('td')]

        rows = table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                entry = {}
                for header, cell in zip(headers, cells):
                    entry[header] = clean_text(cell.text)
                all_data.append({"type": "table_row", "content": entry})
            all_data.append({"type": "empty_line", "content": ""})

    # Extract paragraph data
    paragraphs = soup.find_all(['p', 'div'])
    for para in paragraphs:
        if para.name == 'p' or (para.name == 'div' and 'class' in para.attrs and 'list' in para['class']):
            text = clean_text(para.text)
            if text:
                all_data.append({"type": "paragraph", "content": add_newlines(text)})

    return all_data

def format_output(extracted_data):
    formatted_output = ""
    for item in extracted_data:
        if item['type'] == 'table_row':
            formatted_output += "Table Row:\n"
            for key, value in item['content'].items():
                formatted_output += f"{key}: {value}\n"
            formatted_output += "\n"
        elif item['type'] == 'paragraph':
            formatted_output += "Paragraph:\n"
            formatted_output += item['content'] + "\n\n"
        elif item['type'] == 'empty_line':
            formatted_output += "\n"
    return formatted_output

# Example usage
html_content = """
Your HTML content here
"""

extracted_data = extract_content(html_content)
data = format_output(extracted_data)

# Save the data to a text file
with open('extracted_content.txt', 'w', encoding='utf-8') as file:
    file.write(data)

print("Data has been saved to 'extracted_content.txt'")