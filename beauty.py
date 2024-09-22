from bs4 import BeautifulSoup
import re

# The HTML content you provided
html_content = """[Your HTML content here]"""

soup = BeautifulSoup(html_content, 'html.parser')

# Regex to match the relevant headers
header_pattern = re.compile(r'Part \d+(\.\d+)? of Schedule 1 to the Regulations is amended by adding the following in numerical order:')

# Finding all divs that might contain the headers and entries
divs = soup.find_all('div')

# This list will hold all relevant entries
entries = []
capture = False  # This flag determines whether to start capturing entries

# Loop through each div to process it
for div in divs:
    if header_pattern.search(div.text):  # Check if the div is a header
        capture = True  # Start capturing the entries
    elif capture:
        if re.match(r'\d+', div.text):  # Check if the div text starts with a number
            entries.append(div.text)
        else:
            capture = False  # Stop capturing if the next numbered entry isn't found

# Output the captured entries
for entry in entries:
    print(entry)
