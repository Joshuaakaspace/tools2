import pandas as pd
import json

def clean_dataframe(df):
    """
    Function to strip unnecessary spaces from all string columns in a dataframe.
    """
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

def find_deleted_records(master_df, df, key_col, comparison_cols, json_file_name='deleted_records.json'):
    """
    Function to find records in master_df that are missing from df based on the unique key.
    """
    # Create unique keys
    master_df[key_col] = master_df['ID'].astype(str) + '-' + master_df['Name'].str.strip()
    df[key_col] = df['ID'].astype(str) + '-' + df['Name'].str.strip()
    
    # Perform an inner join to find common records
    common_records = pd.merge(master_df, df, how='inner', on=key_col)
    
    # Identify deleted records by removing common records from master_df
    deleted_records = master_df[~master_df[key_col].isin(common_records[key_col])]
    deleted_records['Status'] = 'DELETED'
    
    # Save deleted records to JSON
    deleted_records_dict = deleted_records.to_dict(orient='records')
    with open(json_file_name, 'w') as json_file:
        json.dump(deleted_records_dict, json_file, indent=4)
    
    # Remove deleted records from master_df
    updated_master_df = master_df[~master_df[key_col].isin(deleted_records[key_col])]
    
    return updated_master_df

def compare_and_update_dataframes(master_df, df, comparison_cols, key_col='unique_key', json_file_name='updated_records.json'):
    """
    Function to compare two dataframes based on a unique key, track changes in specific columns,
    update the master_df with new values, and save the changes to a JSON file.
    """
    # Merge on unique key to align records
    merged_df = pd.merge(master_df, df, how='inner', on=key_col, suffixes=('_old', '_new'))
    
    changes = []
    
    # Check for differences in the comparison columns and update master_df
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
                # Update the master_df with the new value
                master_df.loc[master_df[key_col] == row[key_col], col] = new_value

    # Save changes to JSON file if there are any differences
    if changes:
        with open(json_file_name, 'w') as json_file:
            json.dump(changes, json_file, indent=4)
    
    return master_df, changes

def add_new_records(master_df, df, key_col, json_file_name='added_records.json'):
    """
    Function to find new records in df that are not present in master_df based on the unique key.
    """
    # Identify new records by checking which unique keys in df are not in master_df
    new_records = df[~df[key_col].isin(master_df[key_col])]
    new_records['Status'] = 'ADDED'

    # Convert new records to dictionary for JSON export
    new_records_dict = new_records.to_dict(orient='records')

    # Write new records to a JSON file
    with open(json_file_name, 'w') as json_file:
        json.dump(new_records_dict, json_file, indent=4)

    # Append new records to master_df
    updated_master_df = pd.concat([master_df, new_records], ignore_index=True)

    return updated_master_df

# Main function to perform all operations
def process_master_df(master_df, df, comparison_cols, key_col='unique_key'):
    """
    Function to perform delete, update, and add operations on master_df.
    First, it removes deleted records, then updates records, and finally adds new records.
    """
    # Clean both dataframes
    master_df = clean_dataframe(master_df)
    df = clean_dataframe(df)
    
    # Step 1: Remove deleted records
    master_df = find_deleted_records(master_df, df, key_col, comparison_cols)
    
    # Step 2: Update modified records
    master_df, _ = compare_and_update_dataframes(master_df, df, comparison_cols, key_col)
    
    # Step 3: Add new records
    master_df = add_new_records(master_df, df, key_col)
    
    # Drop the unique key column from the final master_df
    master_df.drop(columns=[key_col], inplace=True)
    
    return master_df

# Example DataFrames
master_df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', 'Bob'],
    'Date of Birth': ['1990-01-01', '1985-06-15', '1992-04-12'],
    'Also Known As': ['Johnny', 'Alicia', 'Bobby']
})

df = pd.DataFrame({
    'ID': [1, 2, 3, 4],  # Bob is unchanged, Alice has updates, and Charlie is new
    'Name': ['John', 'Alice', 'Bob', 'Charlie'],
    'Date of Birth': ['1990-01-01', '1985-06-16', '1992-04-12', '1980-05-20'],
    'Also Known As': ['Johnny', 'Alice', 'Bobby', 'Chuck']
})

# Define the columns to check for changes
comparison_cols = ['Date of Birth', 'Also Known As']

# Process the master dataframe
updated_master_df = process_master_df(master_df, df, comparison_cols)

# Display the final updated master dataframe
print("Final Updated Master DataFrame:")
print(updated_master_df)
