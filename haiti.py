import pandas as pd

# Create dummy data for the three sheets
data1 = {
    'ID': [1, 2, 3, 4],
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Date of Birth': ['1980-01-01', '1985-02-02', '1990-03-03', '1995-04-04'],
    'Also known as': ['Ally', 'Bobby', 'Char', 'Dave']
}

data2 = {
    'ID': [5, 6, 7, 8],
    'Name': ['Eva', 'Frank', 'Grace', 'Hank'],
    'Date of Birth': ['1980-05-05', '1985-06-06', '1990-07-07', '1995-08-08'],
    'Also known as': ['Evie', 'Frankie', 'Gracie', 'Hanky']
}

data3 = {
    'ID': [9, 10, 11],
    'Name': ['Ivy', 'Jack', 'Kate'],
    'Date of Birth': ['1980-09-09', '1985-10-10', '1990-11-11'],
    'Also known as': ['Iv', 'Jacky', 'Katie']
}

sheet1 = pd.DataFrame(data1)
sheet2 = pd.DataFrame(data2)
sheet3 = pd.DataFrame(data3)

# Load custom dataframe (cus_dataframe)
cus_dataframe = pd.DataFrame({
    'ID': [12], 
    'Name': ['John Doe'], 
    'Date of Birth': ['1990-01-01'], 
    'Also known as': ['Johnny']
})

# Function to get max ID from the three sheets
def get_max_id(sheets):
    max_id = -1
    for sheet in sheets:
        if not sheet['ID'].empty:
            max_id = max(max_id, sheet['ID'].max())
    return max_id

# Function to find matching ID and compare records
def match_and_update(cus_record, sheets):
    id_to_check = cus_record['ID'].values[0]
    name_to_check = cus_record['Name'].values[0]
    dob_to_check = cus_record['Date of Birth'].values[0]
    aka_to_check = cus_record['Also known as'].values[0]
    
    for sheet in sheets:
        existing_record = sheet[sheet['ID'] == id_to_check]
        if not existing_record.empty:
            if existing_record['Name'].values[0] == name_to_check:
                # Check for differences in other fields
                if (existing_record['Date of Birth'].values[0] != dob_to_check or
                    existing_record['Also known as'].values[0] != aka_to_check):
                    # Update the corresponding row
                    sheet.loc[sheet['ID'] == id_to_check, ['Date of Birth', 'Also known as']] = dob_to_check, aka_to_check
                    print(f"Record with ID {id_to_check} updated in sheet.")
                else:
                    print(f"Record with ID {id_to_check} matches perfectly, no action needed.")
            else:
                # If name differs, create a new record with new ID
                return False  # Name mismatch found, stop checking further
    return True  # If no mismatch in ID and Name

# List of sheets for easier iteration
sheets = [sheet1, sheet2, sheet3]

# Get the first record of cus_dataframe
cus_record = cus_dataframe.iloc[[0]]

# Check if ID exists in any of the sheets
id_exists = match_and_update(cus_record, sheets)

if not id_exists:
    # If the ID does not exist, find max ID and add the record to the sheet with max ID
    max_id = get_max_id(sheets)
    
    if cus_record['ID'].values[0] <= max_id:
        # If the record's ID is lower than the max ID, update it to a new ID (max_id + 1)
        cus_record['ID'] = max_id + 1
    
    # Insert the new record into the sheet with the lowest max ID
    max_id_sheet = max(sheets, key=lambda x: x['ID'].max())
    max_id_sheet = max_id_sheet.append(cus_record, ignore_index=True)
    print(f"New record added with ID {cus_record['ID'].values[0]} to sheet with max ID.")

# Display the updated sheets for validation
import ace_tools as tools; tools.display_dataframe_to_user(name="Updated Sheet1", dataframe=sheet1)
tools.display_dataframe_to_user(name="Updated Sheet2", dataframe=sheet2)
tools.display_dataframe_to_user(name="Updated Sheet3", dataframe=sheet3)
