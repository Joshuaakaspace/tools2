import pandas as pd
import json

def compare_dataframes(master_df, df, comparison_cols, key_col='unique_key', json_file_name='changed_records.json'):
    """
    Function to compare two dataframes based on a unique key and track changes in specific columns.
    The changes are saved as a JSON file.
    """
    # Create a unique key by concatenating 'ID' and 'Name'
    master_df[key_col] = master_df['ID'].astype(str) + '-' + master_df['Name'].str.strip()
    df[key_col] = df['ID'].astype(str) + '-' + df['Name'].str.strip()
    
    # Merge on unique key to align records
    merged_df = pd.merge(master_df, df, how='inner', on=key_col, suffixes=('_old', '_new'))
    
    changes = []
    
    # Check for differences in the comparison columns
    for index, row in merged_df.iterrows():
        for col in comparison_cols:
            old_value = row[f'{col}_old']
            new_value = row[f'{col}_new']
            if old_value != new_value:
                changes.append({
                    'Unique Key': row[key_col],
                    'Field Name': col,
                    'Old Value': old_value,
                    'New Value': new_value
                })

    # Save changes to JSON file if there are any differences
    if changes:
        with open(json_file_name, 'w') as json_file:
            json.dump(changes, json_file, indent=4)
    
    return changes

# Example DataFrames
master_df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', 'Bob'],
    'Date of Birth': ['1990-01-01', '1985-06-15', '1992-04-12'],
    'Also Known As': ['Johnny', 'Alicia', 'Bobby']
})

df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', 'Bob'],
    'Date of Birth': ['1990-01-01', '1985-06-16', '1992-04-12'],  # Changed DOB for Alice
    'Also Known As': ['Johnny', 'Alice', 'Bobby']  # Changed Also Known As for Alice
})

# Define the columns to check for changes
comparison_cols = ['Date of Birth', 'Also Known As']

# Compare dataframes and generate the JSON file
changed_records = compare_dataframes(master_df, df, comparison_cols)

# Display the changed records
print(changed_records)
