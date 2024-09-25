import pandas as pd
from bs4 import BeautifulSoup

# Your HTML content
html_content = '''
<div id="content">
    <h1 id="wb-cont">Regulations Amending the Special Economic Measures (Haiti) Regulations:&nbsp;SOR/2024-144</h1>
    <ul class="lst-spcd mrgn-lft-lg list-unstyled">
        <li>12	Luckson Elan (born on January&nbsp;6,&nbsp;1988) (also known as Lucson Elan and Jeneral Luckson)</li>
        <li>13	Gabriel Jean-Pierre (born on March&nbsp;31,&nbsp;1984) (also known as Ti-Gabriel)</li>
        <li>14	Ferdens Tilus (born on September&nbsp;15,&nbsp;1995) (also known as Jeneral Meyer and Jeneral Meyè)</li>
    </ul>
    <p><strong>2 Item 1 of Part&nbsp;3 of the schedule to the Regulations is replaced by the following:</strong></p>
    <ul class="lst-spcd mrgn-lft-lg list-unstyled">
        <li>1	Joseph Wilson (born on February&nbsp;28,&nbsp;1993) (also known as Lanmò San Jou)</li>
    </ul>
</div>
'''

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Initialize variables
data = []
current_part = None

# Loop through all elements in the content
for tag in soup.find_all(['p', 'ul']):
    if tag.name == 'p' and 'Part' in tag.text:
        # Extract the part number from the paragraph
        current_part = tag.text.split('Part')[-1].strip().split()[0]
    
    if tag.name == 'ul':
        # Loop through the list items in the unordered list
        for li in tag.find_all('li'):
            # Extract ID
            id_part = li.text.split()[0]
            # Extract name (before the first parenthesis)
            name = li.text.split('(', 1)[0].split('\t')[-1].strip()

            # Try to extract date of birth if present
            dob = None
            if "born on" in li.text:
                dob = li.find(text=lambda x: "born on" in x).split("born on ")[1].split(')')[0].strip()

            # Try to extract aliases if present
            aliases = None
            if "also known as" in li.text:
                aliases = li.find(text=lambda x: "also known as" in x).split("also known as ")[1].split(')')[0].strip()
            
            # Append the extracted information to the list
            data.append({
                'ID': id_part,
                'Name': name,
                'Date of Birth': dob if dob else 'N/A',
                'Also Known As': aliases if aliases else 'N/A',
                'Part': f'Part {current_part}' if current_part else 'Unknown Part'
            })

# Create the dataframe
df = pd.DataFrame(data)

# Display the dataframe
import ace_tools as tools; tools.display_dataframe_to_user(name="Extracted Data with Handling Missing Fields", dataframe=df)
