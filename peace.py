import pandas as pd
import json

def identify_changes(master_df, df2, id_col='ID', name_col='Name', output_prefix='output'):
    # Step 1: Create a copy of master_df as df1
    df1 = master_df.copy()

    # Step 2: Create a unique key by concatenating ID and Name columns
    df1['Unique_Key'] = df1[id_col].astype(str) + '-' + df1[name_col]
    df2['Unique_Key'] = df2[id_col].astype(str) + '-' + df2[name_col]

    # Step 3: Append df2 to df1
    df1_appended = pd.concat([df1, df2], ignore_index=True)

    # Step 4: Handle removals where records are identical
    removed_records = []
    for key in df1['Unique_Key']:
        df1_rows = df1[df1['Unique_Key'] == key]
        df2_rows = df2[df2['Unique_Key'] == key]
        if not df2_rows.empty:
            # If all fields match, mark as removed
            if df1_rows.iloc[0].equals(df2_rows.iloc[0]):
                removed_records.append(df1_rows.iloc[0].to_dict())

    # Step 5: Handle updates where only some fields differ
    updated_records = []
    for key in df1['Unique_Key']:
        df1_rows = df1[df1['Unique_Key'] == key]
        df2_rows = df2[df2['Unique_Key'] == key]
        if not df2_rows.empty:
            # Check if fields differ
            if not df1_rows.iloc[0].equals(df2_rows.iloc[0]):
                # Remove record from df2 and add to updated records
                df2 = df2[df2['Unique_Key'] != key]
                updated_records.append(df2_rows.iloc[0].to_dict())

    # Step 6: Handle additions by finding keys present in df2 but not in master_df
    added_records = df2[~df2['Unique_Key'].isin(master_df['Unique_Key'])].to_dict(orient='records')

    # Step 7: Save results to JSON files
    with open(f'{output_prefix}_added_records.json', 'w') as f:
        json.dump(added_records, f, indent=4)

    with open(f'{output_prefix}_updated_records.json', 'w') as f:
        json.dump(updated_records, f, indent=4)

    with open(f'{output_prefix}_removed_records.json', 'w') as f:
        json.dump(removed_records, f, indent=4)

    # Return summary of changes
    return {
        "added": added_records,
        "updated": updated_records,
        "removed": removed_records
    }

# Example usage:
data_master = {
    'ID': [1, 2, 3],
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Date of Birth': ['1990-01-01', '1985-05-15', '1992-12-12'],
    'Also Known As': ['A', 'B', 'C']
}

data_other = {
    'ID': [2, 3, 4],
    'Name': ['Bob', 'Charlie', 'David'],
    'Date of Birth': ['1985-06-01', '1992-12-12', '1993-03-01'],
    'Also Known As': ['BB', 'C', 'D']
}

master_df = pd.DataFrame(data_master)
df2 = pd.DataFrame(data_other)

# Call the function
changes_summary = identify_changes(master_df, df2, output_prefix='master_diff')
print("Summary of Changes:")
print(changes_summary)
