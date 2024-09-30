# Updated sub_pattern to capture additional text after the recognized patterns
def extract_info_updated(text):
    # Updated name pattern to capture names with two or more words
    name_pattern = r"(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)"  # Captures multi-word names
    aka_pattern = r"aka\s([A-Za-z]+)"  # Captures 'aka Josh'
    
    # Updated sub pattern to include extra details like 'blackwaters, sandpotters'
    sub_pattern = r"(and any successor(?:, sub-unit, or subsidiary thereof)?(?:\s[\w,\s]+)?)"

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

# Sample DataFrame with the updated example
df = pd.DataFrame({
    'Name': [
        'Peter Parker aka Spidey and any successor, sub-unit, or subsidiary thereof blackwaters, sandpotters'
    ]
})

# Apply the updated extract_info function to the 'Name' column and create new columns
df[['Full Name', 'AKA', 'Sub']] = df['Name'].apply(lambda x: pd.Series(extract_info_updated(x)))

# Display the updated DataFrame
import ace_tools as tools; tools.display_dataframe_to_user(name="Updated DataFrame with Full Name, AKA, Sub", dataframe=df)
