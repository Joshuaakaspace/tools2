# Updated function to handle names without capturing "and successor"
def extract_info_updated(text):
    # Updated name pattern to capture names up until the point of specific keywords like 'and successor'
    name_pattern = r"([A-Z]+[A-Za-z\s\.]+)(?=\s(and|or)\s(successor|sub-unit|subsidiary))"
    aka_pattern = r"aka\s([A-Za-z]+)"  # Captures 'aka Josh'
    
    # Updated sub pattern to include extra details like 'blackwaters, sandpotters'
    sub_pattern = r"(and successor(?:, sub-unit, or subsidiary thereof)?(?:\s[\w,\s]+)?)"

    # Extract name
    name_match = re.search(name_pattern, text)
    name = name_match.group(0) if name_match else None

    # Extract aka
    aka_match = re.search(aka_pattern, text)
    aka = aka_match.group(1) if aka_match else None

    # Extract sub
    sub_match = re.search(sub_pattern, text)
    sub = sub_match.group(0) if sub_match else None

    return {
        "Full Name": name,
        "AKA": aka,
        "Sub": sub
    }

# Updating the input DataFrame with the new example including '.Ltd'
df = pd.DataFrame({
    'Name': [
        'OTOBOT Project Group .Ltd and successor, sub-unit, or subsidiary thereof'
    ]
})

# Apply the updated extract_info function to the 'Name' column and create new columns
df[['Full Name', 'AKA', 'Sub']] = df['Name'].apply(lambda x: pd.Series(extract_info_updated(x)))

# Display the updated DataFrame
import ace_tools as tools; tools.display_dataframe_to_user(name="Updated DataFrame with Full Name, AKA, Sub", dataframe=df)
