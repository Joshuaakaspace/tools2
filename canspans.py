import re
import pandas as pd
from bs4 import BeautifulSoup

# HTML content with some missing 'Also Known As' or 'born on' data for testing robustness
html_content = """
<ul class="lst-spcd mrgn-lft-lg list-unstyled">
    <li>120 Nikolai Aleksandrovich LUKASHENKO (born on August 31, 2004) (also known as Mikalay Alyaksandravich LUKASHENKA and Kolya LUKASHENKO)</li>
    <li>121 Yuliya Aleksandrovna BLIZNIUK (also known as Yuliya Aliaksandrauna BLIZNIUK, Julija Aleksandrovna BLIZNJUK)</li>
    <li>122 Vitali Viktorovich SINILO (born on May 15, 1975)</li>
    <li>123 Iryna Vasilyeuna PRADUN (born on May 21, 1974)</li>
    <li>124 Valiantsina Piatrouna NOVIKAVA (born on October 12, 1978) (also known as Valentina Petrovna NOVIKOVA)</li>
    <li>125 Vadzim Ivanavich MAZOL</li>
    <li>126 Aliaksandr Viktaravich ABASHYN (born on November 19, 1960)</li>
</ul>
"""

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')
ul_tag = soup.find('ul', class_='lst-spcd mrgn-lft-lg list-unstyled')

# Initialize an empty list to store the data
data = []

# Define a regex pattern to extract the desired information
pattern = re.compile(r'^(\d+)\s(.*?)(?:\s\(born on\s(.*?)\))?(\s\(also known as\s(.*?)\))?')

# Iterate through each li element and apply the regex
for li in ul_tag.find_all('li'):
    match = pattern.search(li.text.replace(u'\xa0', u' '))
    if match:
        id_ = match.group(1)
        name = match.group(2)
        dob = match.group(3) if match.group(3) else ''
        aka = match.group(5) if match.group(5) else ''
        data.append({
            'ID': id_,
            'Name': name.strip(),
            'Date of Birth': dob.strip(),
            'Also Known As': aka.strip(),
            'Status': ''
        })

# Create a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)
