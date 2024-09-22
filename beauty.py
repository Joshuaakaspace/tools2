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


import re

# Example list of strings extracted from the HTML document
data = [
    "1 Part 1 of Schedule 1 to the Special Economic Measures (Belarus) Regulations is amended by adding the following in numerical order:",
    "120 Nikolai Aleksandrovich LUKASHENKO (born on August 31, 2004) (also known as Mikalay Alyaksandravich LUKASHENKA and Kolya LUKASHENKO)",
    "121 Yuliya Aleksandrovna BLIZNIUK (born on September 23, 1971) (also known as Yuliya Aliaksandrauna BLIZNIUK, Julija Aleksandrovna BLIZNJUK and Julija Aljaksandrauna BLIZNJUK)",
    "2 Part 1.1 of Schedule 1 to the Regulations is amended by adding the following in numerical order:",
    "93 Oleg Grigorievich MISHCHENKO (born on August 11, 1968) (also known as Aleh Ryhoravich MISHCHANKA)",
    "94 Pavel Nikolaevich MURAVEIKO (born on September 26, 1971)",
    "3 Part 2 of Schedule 1 to the Regulations is amended by adding the following in numerical order:",
    "71 Design Bureau “Display” JSC",
    "4 Part 3 of Schedule 1 to the Regulations is amended by adding the following in numerical order:",
    "2 Open Joint Stock Company \"Minsk Electrotechnical Plant named after V.I. Kozlov\" (also known as OJSC “Minsk Electrotechnical Plant named after V.I. Kozlov” and OJSC “METP NAMED AFTER V.I. KOZLOV”)"
]

# Regex to match headers indicating the beginning of sections
header_pattern = re.compile(r'Part \d+(\.\d+)? of Schedule \d+ to the Regulations is amended by adding the following in numerical order:')

# List to hold all the extracted entries
entries = []

# Variable to keep track of whether we are currently capturing entries
capturing = False

for line in data:
    if header_pattern.search(line):
        capturing = True  # Start capturing entries after this line
    elif capturing:
        if re.match(r'^\d+', line.strip()):  # Line starts with one or more digits
            entries.append(line)
        else:
            capturing = False  # Stop capturing if a line doesn't start with a number

# Print the extracted entries
for entry in entries:
    print(entry)
