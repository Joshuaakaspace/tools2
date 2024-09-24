import pandas as pd
import json

def update_master_and_save_json(master_df, df, id_col='ID', name_col='Name', json_file_name='added_records.json'):
    # Create a unique key by concatenating 'ID' and 'Name'
    master_df['unique_key'] = master_df[id_col].astype(str) + '-' + master_df[name_col]
    df['unique_key'] = df[id_col].astype(str) + '-' + df[name_col]

    # Find new records by checking which unique keys in df are not in master_df
    new_records = df[~df['unique_key'].isin(master_df['unique_key'])].copy()

    # Add a label column 'Status' and set it to 'ADDED' for new records
    new_records['Status'] = 'ADDED'

    # Convert new records to dictionary for JSON export
    new_records_dict = new_records.to_dict(orient='records')

    # Write new records to a JSON file
    with open(json_file_name, 'w') as json_file:
        json.dump(new_records_dict, json_file, indent=4)

    # Append new records to master_df
    updated_master_df = pd.concat([master_df, new_records], ignore_index=True)

    # Optionally, you can drop the 'unique_key' column if it's not needed
    updated_master_df.drop(columns=['unique_key'], inplace=True)

    return updated_master_df

# Example usage
master_df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', 'Bob'],
    'Age': [25, 30, 22]
})

df = pd.DataFrame({
    'ID': [1, 2, 4],
    'Name': ['John', 'Alice', 'Charlie'],
    'Age': [25, 30, 28]
})

# Call the function to update the master dataframe and save new records to JSON
updated_master_df = update_master_and_save_json(master_df, df)

# Display the updated master dataframe
print(updated_master_df)
