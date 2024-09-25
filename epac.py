# Let's test the code snippet provided with a simulation

import re
import pandas as pd
from bs4 import BeautifulSoup

# Sample HTML content with PART numbers included
html_content = '''<div class="Schedule" id="1261281"><header><h2 class="scheduleLabel" id="h-1261282"><span class="scheduleLabel">SCHEDULE 1</span><span class="OriginatingRef">(Section 2 and subsections 8(1) and (2))</span><span class="scheduleTitleText">
Persons</span><br></h2></header><figure><figcaption><p><span class="HLabel">PART 1</span></p><p><span class="HTitleText1">Individuals — Gross Human Rights Violations</span></p>SOR/2022-49, s. 5</figcaption><ul class="noBullet"><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">1</span>&nbsp;</div><div class="listItemText2">Luckson Elan (born on January 6, 1988) (also known as Lucson Elan and Jeneral Luckson)</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">2</span>&nbsp;</div><div class="listItemText2">Dmitry Vladimirovich Balaba</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">3</span>&nbsp;</div><div class="listItemText2">Aleksandr Petrovich Barsukov</div></div></li></ul><p><span class="HLabel">PART 1.1</span></p><ul class="noBullet"><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">4</span>&nbsp;</div><div class="listItemText2">Yelena Nikolaevna Dmukhailo</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">5</span>&nbsp;</div><div class="listItemText2">Vadim Dmitriyevich Ipatov</div></div></li></ul></div>'''

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all the PART numbers
part_elements = soup.find_all('span', class_='HLabel')

# Extract all the entities with associated IDs
ids = [item.get_text() for item in soup.find_all('span', class_='lawlabel')]
names_list = [item.get_text() for item in soup.find_all('div', class_='listItemText2')]

# Define regular expressions to extract Name, Date of Birth, and Also Known As
dob_regex = r"\(born on ([\w\s,]+)\)"
aka_regex = r"\(also known as ([\w\s,]+)\)"

# Function to extract details from each entity, with the PART number
def extract_details(text, id_value, part_value):
    name = re.sub(r"\(.*?\)", "", text).strip()  # Remove the parentheses
    dob_match = re.search(dob_regex, text)
    aka_match = re.search(aka_regex, text)
    
    date_of_birth = dob_match.group(1) if dob_match else None
    also_known_as = aka_match.group(1) if aka_match else None
    
    return {"ID": id_value, "Name": name, "Date of Birth": date_of_birth, "Also Known As": also_known_as, "PART": part_value}

# Initialize list for storing the data
data = []

# Keep track of the current PART value
current_part = None

# Find each part and extract entities listed under it
for part_element in soup.find_all('span', class_='HLabel'):
    current_part = part_element.get_text()  # Set the current part
    # Find the next sibling UL that contains the entities
    next_ul = part_element.find_next('ul', class_='noBullet')
    
    # Extract IDs and names from the UL element
    if next_ul:
        for list_item in next_ul.find_all('li'):
            id_value = list_item.find('span', class_='lawlabel').get_text()
            name_value = list_item.find('div', class_='listItemText2').get_text()
            id_cleaned = re.sub(r'\D', '', id_value)
            data.append(extract_details(name_value, id_cleaned, current_part))

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(data)

import ace_tools as tools; tools.display_dataframe_to_user(name="Test Individual Details with Parts", dataframe=df)
