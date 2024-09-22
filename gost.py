# Since the issue persists, I will now recheck the regex pattern and parsing logic carefully.

# Define the regex pattern once again to ensure it captures both 'born on' and 'also known as' elements properly
pattern = re.compile(r'(\d+)\s([^()]+)\s*(\(born on\s([^)]+)\))?\s*(\(also known as\s([^)]+)\))?')

# Iterate through each li element and apply the regex with corrections
data = []
for li in ul_tag.find_all('li'):
    text = li.get_text()
    match = pattern.search(text)
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
            'Status': ''
        })

# Creating the corrected DataFrame and displaying
df = pd.DataFrame(data)
tools.display_dataframe_to_user(name="Final Corrected Extracted Information", dataframe=df)
