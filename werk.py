import pandas as pd

# Sample data for master_df and df2 to test the approach
data_master = {
    'ID': [1, 2, 3, 4],
    'Name': ['John', 'Alice', 'Bob', 'Eve'],
    'Date of Birth': ['1990-01-01', '1985-05-05', '1992-12-12', '1980-07-07'],
    'Also Known As': ['Johnny', 'Ally', 'Robert', 'Eve']
}

data_df2 = {
    'ID': [1, 2, 3, 5],  # 5 is new, 4 is missing (deleted)
    'Name': ['John', 'Alice', 'Bob', 'Charlie'],
    'Date of Birth': ['1990-01-01', '1985-05-05', '1993-12-12', '1975-08-08'],  # Bob's DOB changed
    'Also Known As': ['Johnny', 'Ally', 'Rob', 'Charlie']
}

# Creating DataFrames
master_df = pd.DataFrame(data_master)
df2 = pd.DataFrame(data_df2)

# Step 1: Create the unique key by concatenating 'Name' and 'ID' in both dataframes
master_df['unique_key'] = master_df['Name'] + master_df['ID'].astype(str)
df2['unique_key'] = df2['Name'] + df2['ID'].astype(str)

# Step 2: Identify Updated Records
updated_records = []
for idx, row in master_df.iterrows():
    unique_key = row['unique_key']
    df2_matching_row = df2[df2['unique_key'] == unique_key]
    
    if not df2_matching_row.empty:
        # Check if columns have different values (other than ID and Name)
        if not row[['Date of Birth', 'Also Known As']].equals(df2_matching_row[['Date of Birth', 'Also Known As']].iloc[0]):
            updated_records.append(df2_matching_row.iloc[0])  # Place updated row from df2
            master_df.drop(index=idx, inplace=True)  # Remove the row from master_df (treated as updated)

# Step 3: Identify Deleted Records
deleted_records = master_df[~master_df['unique_key'].isin(df2['unique_key'])]  # Records in master_df but not in df2

# Step 4: Identify Added Records
added_records = df2[~df2['unique_key'].isin(master_df['unique_key'])]  # Records in df2 but not in master_df

# Display the results to check
updated_records_df = pd.DataFrame(updated_records)
updated_records_df, deleted_records, added_records
