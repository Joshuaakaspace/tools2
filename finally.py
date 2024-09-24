import pandas as pd
import json

def update_master(master_df, added_df, removed_df, changed_df, key_col='unique_key'):
    # Step 1: Add the new records to master_df
    updated_master_df = pd.concat([master_df, added_df], ignore_index=True)
    
    # Step 2: Remove the deleted records from master_df
    updated_master_df = updated_master_df[~updated_master_df[key_col].isin(removed_df[key_col])]
    
    # Step 3: Update changed records in master_df
    for index, changed_row in changed_df.iterrows():
        # Find the index of the record in master_df by the unique key
        record_index = updated_master_df[updated_master_df[key_col] == changed_row[key_col]].index
        if not record_index.empty:
            # Update the record with the values from the changed_df
            updated_master_df.loc[record_index, changed_row.index] = changed_row.values

    return updated_master_df

# Example DataFrames for added, removed, and changed records
master_df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', 'Bob'],
    'Date of Birth': ['1990-01-01', '1985-06-15', '1992-04-12'],
    'Also Known As': ['Johnny', 'Alicia', 'Bobby'],
    'unique_key': ['1-John', '2-Alice', '3-Bob']
})

added_df = pd.DataFrame({
    'ID': [4],
    'Name': ['Charlie'],
    'Date of Birth': ['1990-05-10'],
    'Also Known As': ['Chuck'],
    'unique_key': ['4-Charlie']
})

removed_df = pd.DataFrame({
    'ID': [3],
    'Name': ['Bob'],
    'Date of Birth': ['1992-04-12'],
    'Also Known As': ['Bobby'],
    'unique_key': ['3-Bob']
})

changed_df = pd.DataFrame({
    'ID': [2],
    'Name': ['Alice'],
    'Date of Birth': ['1985-06-16'],  # Changed date of birth
    'Also Known As': ['Alice'],       # Changed 'Also Known As'
    'unique_key': ['2-Alice']
})

# Update the master dataframe
updated_master_df = update_master(master_df, added_df, removed_df, changed_df)

# Display the updated master dataframe
print("Updated Master DataFrame:")
print(updated_master_df)
