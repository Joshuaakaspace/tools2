# Running the previous solution to check if the update and logic works as expected

# Sample master DataFrame (assuming it already exists)
master_data = {
    'ID': ['120', '121', '124', '125', '126'],
    'Name': ['Nikolai Aleksandrovich LUKASHENKO', 'Yuliya Aleksandrovna BLIZNIUK', 
             'Valiantsina Piatrouna NOVIKAVA', 'Vadzim Ivanavich MAZOL', 'Aliaksandr Viktaravich ABASHYN'],
    'Date of Birth': ['August 31, 2004', '', 'October 12, 1978', '', 'November 19, 1960'],
    'Also Known As': ['Mikalay Alyaksandravich LUKASHENKA and Kolya LUKASHENKO', 
                      'Yuliya Aliaksandrauna BLIZNIUK', 
                      'Valentina Petrovna NOVIKOVA', '', ''],
    'Status': ['Active', 'Active', 'Active', 'Active', 'Active'],
    'Part': ['Part 1', 'Part 1', 'Part 2', 'Part 2', 'Part 2']
}
master_df = pd.DataFrame(master_data)

# Concatenate Name and ID to form a unique key in both master_df and df
master_df['Unique Key'] = master_df['Name'] + ' ' + master_df['ID']
df['Unique Key'] = df['Name'] + ' ' + df['ID']

# Function to update master_df based on new records in df
def update_master_df(master_df, df):
    # Records to add (where the unique key does not exist in the master DataFrame)
    records_to_add = df[~df['Unique Key'].isin(master_df['Unique Key'])]
    
    # Records to update (where the unique key exists but other details differ)
    records_to_update = df[df['Unique Key'].isin(master_df['Unique Key'])]
    for index, row in records_to_update.iterrows():
        master_index = master_df[master_df['Unique Key'] == row['Unique Key']].index[0]
        for col in ['Date of Birth', 'Also Known As', 'Status', 'Part']:
            if master_df.at[master_index, col] != row[col]:
                master_df.at[master_index, col] = row[col]
    
    # Remove records where all details match
    for index, row in records_to_update.iterrows():
        master_index = master_df[master_df['Unique Key'] == row['Unique Key']].index[0]
        if all(master_df.at[master_index, col] == row[col] for col in ['Date of Birth', 'Also Known As', 'Status', 'Part']):
            master_df = master_df.drop(master_index)
    
    # Add new records to the master DataFrame
    master_df = pd.concat([master_df, records_to_add], ignore_index=True)
    
    return master_df

# Update the master DataFrame with new records from df
updated_master_df = update_master_df(master_df, df)

# Display the updated master DataFrame
tools.display_dataframe_to_user(name="Updated Master DataFrame", dataframe=updated_master_df)
