# Final single code to extract ID, Name, Date of Birth, Also Known As, and Part number

def extract_details_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # Find all <p> and <ul> tags containing individual/entity details
    parts = soup.find_all(['p', 'ul'])

    current_part = None
    for part in parts:
        text = part.get_text()

        # Detect Part number in the text
        part_match = re.search(r'Part\s+(\d+(\.\d+)?)', text)
        if part_match:
            current_part = part_match.group(0)

        # Extract individual/entity details from <ul> tags
        if part.name == 'ul':
            for li in part.find_all('li'):
                li_text = li.get_text()

                # Extract ID
                id_match = re.match(r'^(\d+)', li_text)
                id_num = id_match.group(1) if id_match else None

                # Extract Name, Date of Birth, and Also Known As
                name, dob, also_known_as = extract_individual_details(li_text)
                
                if name and dob and id_num:
                    data.append({
                        'ID': id_num,
                        'Name': name,
                        'Date of Birth': dob,
                        'Also Known As': also_known_as,
                        'Part': current_part
                    })

    return pd.DataFrame(data)

# Helper function to extract individual/entity details
def extract_individual_details(text):
    # Extract Name
    name_match = re.match(r'^\d+\s+(.+?)\s*\(born', text)
    name = name_match.group(1) if name_match else None

    # Extract Date of Birth
    dob_match = re.search(r'born on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})', text)
    dob = dob_match.group(1) if dob_match else None

    # Extract Also Known As (aliases) - within parentheses after the date of birth
    aka_match = re.search(r'\(also known as (.+?)\)', text)
    also_known_as = aka_match.group(1) if aka_match else None

    return name, dob, also_known_as

# Extract details from the HTML
df_with_id = extract_details_from_html(html)

# Display the final extracted DataFrame with all details
tools.display_dataframe_to_user(name="Final Extracted Individual and Entity Details", dataframe=df_with_id)
