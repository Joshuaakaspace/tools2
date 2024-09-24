# Adjusting the logic to ensure correct extraction of parts and list items

# Parsing the HTML content again
soup = BeautifulSoup(html_content, 'html.parser')

# Initialize the list to store the data
data = []

# Patterns for part numbers and list items
part_pattern = re.compile(r"(Part\s\d+\s+of\s+Schedule\s\d+)")
item_pattern = re.compile(r'(\d+)\s([^()]+)\s*(\(born on\s([^)]+)\))?\s*(\(also known as\s([^)]+)\))?')

# Find all the <p> tags with the part descriptions
for part_tag in soup.find_all('p'):
    part_text = part_tag.get_text()
    part_match = part_pattern.search(part_text)
    
    if part_match:
        # Extract the part number text
        part_number = part_match.group(0)
        
        # Find the corresponding <ul> list after the part <p> tag
        ul_tag = part_tag.find_next_sibling('ul')
        if ul_tag:
            for li in ul_tag.find_all('li'):
                li_text = li.get_text()
                match = item_pattern.search(li_text)
                if match:
                    id_ = match.group(1)
                    name = match.group(2).strip()
                    dob = match.group(4) if match.group(4) else ''
                    aka = match.group(6) if match.group(6) else ''
                    data.append({
                        'ID': id_,
                        'Name': name,
                        'Date of Birth': dob,
                        'Also Known As': aka,
                        'Status': '',
                        'Part': part_number
                    })

# Create the DataFrame with the extracted data
df = pd.DataFrame(data)

# Display the DataFrame
tools.display_dataframe_to_user(name="Extracted Data with Parts", dataframe=df)
