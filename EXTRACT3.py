# Modify the extraction function to include the ID as well
def extract_details_from_html_with_id(html):
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

# Step 2: Extract details from the HTML, including the ID
df_with_id = extract_details_from_html_with_id(html)

# Display the extracted DataFrame with ID
tools.display_dataframe_to_user(name="Extracted Individual and Entity Details with ID", dataframe=df_with_id)
