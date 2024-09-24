import pandas as pd
import json

# Sample data for master_df and other_df
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

# Create DataFrames
master_df = pd.DataFrame(data_master)
other_df = pd.DataFrame(data_other)

# Create a unique key by concatenating 'ID' and 'Name' columns
master_df['Unique_Key'] = master_df['ID'].astype(str) + '-' + master_df['Name']
other_df['Unique_Key'] = other_df['ID'].astype(str) + '-' + other_df['Name']

# Scenario 1: Add records to master_df that don't exist (based on unique key)
new_records = other_df[~other_df['Unique_Key'].isin(master_df['Unique_Key'])]
new_records_json = new_records.to_dict(orient='records')

# Update master_df with new records
master_df = pd.concat([master_df, new_records], ignore_index=True)

# Save new records to JSON
with open('new_records.json', 'w') as f:
    json.dump(new_records_json, f, indent=4)

# Scenario 2: Update records in master_df where Unique_Key exists but data differs
updated_records = []

for index, row in other_df.iterrows():
    if row['Unique_Key'] in master_df['Unique_Key'].values:
        master_row = master_df.loc[master_df['Unique_Key'] == row['Unique_Key']]
        if not row.equals(master_row.iloc[0]):
            # Update the record in master_df
            master_df.loc[master_df['Unique_Key'] == row['Unique_Key'], ['Date of Birth', 'Also Known As']] = row[['Date of Birth', 'Also Known As']]
            updated_records.append(row.to_dict())

# Save updated records to JSON
with open('updated_records.json', 'w') as f:
    json.dump(updated_records, f, indent=4)

# Scenario 3: Remove records from master_df where Unique_Key matches and all fields match
removed_records = []

for index, row in master_df.iterrows():
    if row['Unique_Key'] in other_df['Unique_Key'].values:
        other_row = other_df.loc[other_df['Unique_Key'] == row['Unique_Key']]
        if row.equals(other_row.iloc[0]):
            removed_records.append(row.to_dict())
            master_df = master_df[master_df['Unique_Key'] != row['Unique_Key']]

# Save removed records to JSON
with open('removed_records.json', 'w') as f:
    json.dump(removed_records, f, indent=4)

# Remove the Unique_Key column for the final master_df
master_df = master_df.drop(columns=['Unique_Key'])

# Display the updated master_df
print("Updated Master DataFrame:")
print(master_df)
