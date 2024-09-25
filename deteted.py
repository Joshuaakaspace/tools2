import pandas as pd
from bs4 import BeautifulSoup
import re

# Example HTML input
html = '<p><strong>1 Item 57 of  Part 2 of the Schedule to the <cite>Special Economic Measures (Venezuela) Regulations</cite></strong><sup id="footnoteRef.51492"> <a class="fn-lnk" href="#footnote.51492"><span class="wb-inv">footnote </span>1</a></sup><strong> is repealed.</strong></p>'

# Sample master DataFrame
data = {
    'ID': [101, 102, 103],
    'Name': ['John Doe', 'Jane Smith', 'Alice Brown'],
    'Date of Birth': ['1980-01-01', '1990-05-12', '1975-03-23'],
    'Also Known As': ['JD', 'JS', 'AB'],
    'Part': [2, 1, 2]
}
master_df = pd.DataFrame(data)

# Step 1: Parse the HTML, ensure 'repealed' is present, and extract Item and Part numbers
def extract_item_part(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    # Check if 'repealed' is present
    if 'repealed' in text:
        # Extract Item and Part numbers using regex
        item_match = re.search(r'Item\s+(\d+)', text)
        part_match = re.search(r'Part\s+(\d+)', text)

        item_number = int(item_match.group(1)) if item_match else None
        part_number = int(part_match.group(1)) if part_match else None

        return item_number, part_number
    return None, None

# Step 2: Check master_df for matching Item and Part, and remove the entry
def remove_entry(item, part, df):
    if item is not None:
        # Remove based on the Part column, assuming the Part is the key column for deletion
        if part is not None:
            df = df[df['Part'] != part]
        else:
            # If no part is specified, simply remove rows that match only the item (if applicable)
            df = df[df['Part'] != item]
    return df

# Extract item and part from the HTML
item_number, part_number = extract_item_part(html)

# Remove the relevant row from the master_df
updated_df = remove_entry(item_number, part_number, master_df)

# Display the updated DataFrame
import ace_tools as tools; tools.display_dataframe_to_user(name="Updated Master DataFrame", dataframe=updated_df)
