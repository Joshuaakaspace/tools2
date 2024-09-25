import re
import pandas as pd
from bs4 import BeautifulSoup

# Sample HTML content
html_content = '''<div class="Schedule" id="1261281"><header><h2 class="scheduleLabel" id="h-1261282"><span class="scheduleLabel">SCHEDULE 1</span><span class="OriginatingRef">(Section 2 and subsections 8(1) and (2))</span><span class="scheduleTitleText">
Persons</span><br></h2></header><figure><figcaption><p><span class="HLabel">PART 1</span></p><p><span class="HTitleText1">Individuals — Gross Human Rights Violations</span></p>SOR/2022-49, s. 5</figcaption><ul class="noBullet"><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">1</span>&nbsp;</div><div class="listItemText2">Luckson Elan (born on January 6, 1988) (also known as Lucson Elan and Jeneral Luckson)</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">2</span>&nbsp;</div><div class="listItemText2">Dmitry Vladimirovich Balaba</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">3</span>&nbsp;</div><div class="listItemText2">Aleksandr Petrovich Barsukov</div></div></li></ul></div>'''

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all the text items from <div class="listItemText2"> tags
names_list = [item.get_text() for item in soup.find_all('div', class_='listItemText2')]

# Define regular expressions to extract Name, Date of Birth, and Also Known As
dob_regex = r"\(born on ([\w\s,]+)\)"
aka_regex = r"\(also known as ([\w\s,]+)\)"

# Function to extract details from each item
def extract_details(text):
    name = re.sub(r"\(.*?\)", "", text).strip()  # Remove the parentheses
    dob_match = re.search(dob_regex, text)
    aka_match = re.search(aka_regex, text)
    
    date_of_birth = dob_match.group(1) if dob_match else None
    also_known_as = aka_match.group(1) if aka_match else None
    
    return {"Name": name, "Date of Birth": date_of_birth, "Also Known As": also_known_as}

# Extract details for all individuals
data = [extract_details(text) for text in names_list]

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
import ace_tools as tools; tools.display_dataframe_to_user(name="Individual Details", dataframe=df)
