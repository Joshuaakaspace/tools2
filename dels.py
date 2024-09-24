import pandas as pd
import json

def process_deleted_records(master_df, df, comparison_cols, json_file_name='deleted_records.json'):
    """
    Function to find deleted records, label them as DELETED, save to JSON, and remove from master_df.
    This version uses an inner join to optimize the process.
    """
    # Strip spaces from all string columns in both dataframes
    master_df = master_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Perform an inner join to find common records
    common_records = pd.merge(master_df, df, how='inner', on=comparison_cols)

    # Identify deleted records by removing common records from master_df
    deleted_records = master_df[~master_df[comparison_cols].apply(tuple, axis=1).isin(common_records[comparison_cols].apply(tuple, axis=1))]

    # Label the deleted records as 'DELETED'
    deleted_records['Status'] = 'DELETED'

    # Save deleted records to a JSON file
    deleted_records_dict = deleted_records.to_dict(orient='records')
    with open(json_file_name, 'w') as json_file:
        json.dump(deleted_records_dict, json_file, indent=4)

    # Remove deleted records from master_df
    updated_master_df = master_df[~master_df[comparison_cols].apply(tuple, axis=1).isin(deleted_records[comparison_cols].apply(tuple, axis=1))]

    return updated_master_df

# Example usage
master_df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', ' Bob '],  # Spaces in 'Bob'
    'Date of Birth': ['1990-01-01', '1985-06-15', '1992-04-12'],
    'Also Known As': ['Johnny', 'Alicia', 'Bobby']
})

df = pd.DataFrame({
    'ID': [1, 2],
    'Name': ['John', 'Alice'],  # Bob is missing
    'Date of Birth': ['1990-01-01', '1985-06-15'],
    'Also Known As': ['Johnny', 'Alicia']
})

# Define the columns you want to compare
comparison_cols = ['ID', 'Name', 'Date of Birth', 'Also Known As']

# Process deleted records
updated_master_df = process_deleted_records(master_df, df, comparison_cols)

# Display the updated master dataframe
print(updated_master_df)
