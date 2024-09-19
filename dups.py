import pandas as pd
import json
from fuzzywuzzy import fuzz

# Load JSON data
def load_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return pd.DataFrame(data)

# Case-insensitive comparison
def normalize_string(s):
    return s.strip().lower() if isinstance(s, str) else s

# Check if two records are 100% or 90% duplicates
def is_duplicate(row1, row2, threshold=90):
    # Normalize string fields for comparison
    fields_to_check = ['name', 'dob', 'pob', 'reason', 'rank', 'position'] # Adjust as needed
    matches = []
    
    for field in fields_to_check:
        val1 = normalize_string(row1.get(field, ''))
        val2 = normalize_string(row2.get(field, ''))
        if val1 and val2:
            match_score = fuzz.ratio(val1, val2)  # Fuzzy matching for partial matches
            matches.append(match_score >= threshold)
        else:
            matches.append(val1 == val2)  # Handle missing or empty values
    
    return all(matches)  # Returns True if all fields match within the threshold

# Compare completeness of two records
def more_complete_record(row1, row2):
    filled_fields_1 = sum(bool(row1.get(field)) for field in row1)
    filled_fields_2 = sum(bool(row2.get(field)) for field in row2)
    
    # Keep the record with more filled fields
    return row1 if filled_fields_1 >= filled_fields_2 else row2

# Remove duplicates from the dataframe
def drop_duplicates(df):
    unique_records = []
    
    while not df.empty:
        row = df.iloc[0]
        df = df.iloc[1:]  # Remove the current row from the dataframe
        
        # Compare against all remaining rows
        duplicates = df.apply(lambda r: is_duplicate(row, r), axis=1)
        if duplicates.any():
            # Find duplicate row(s)
            dup_rows = df[duplicates]
            
            # Compare and keep the more complete record
            for _, dup_row in dup_rows.iterrows():
                row = more_complete_record(row, dup_row)
                
            # Remove duplicates from dataframe
            df = df[~duplicates]
        
        # Append the unique or best record to the list
        unique_records.append(row)
    
    return pd.DataFrame(unique_records)

# Example usage
json_file = 'your_data.json'  # Replace with your JSON file path
df = load_json(json_file)
cleaned_df = drop_duplicates(df)

# Save back to JSON if needed
cleaned_df.to_json('cleaned_data.json', orient='records', indent=2)
