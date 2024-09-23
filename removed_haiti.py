# Updated function to check for matching record and remove if identical
def match_and_update_or_remove(cus_record, sheets):
    id_to_check = cus_record['ID'].values[0]
    name_to_check = cus_record['Name'].values[0]
    dob_to_check = cus_record['Date of Birth'].values[0]
    aka_to_check = cus_record['Also known as'].values[0]
    
    for sheet in sheets:
        existing_record = sheet[sheet['ID'] == id_to_check]
        if not existing_record.empty:
            if (existing_record['Name'].values[0] == name_to_check and
                existing_record['Date of Birth'].values[0] == dob_to_check and
                existing_record['Also known as'].values[0] == aka_to_check):
                # If all fields match, remove the record
                sheet.drop(sheet[sheet['ID'] == id_to_check].index, inplace=True)
                print(f"Record with ID {id_to_check} matches perfectly. It has been removed.")
                return True  # Record was found and removed
            elif existing_record['Name'].values[0] == name_to_check:
                # Check for differences in other fields and update if necessary
                if (existing_record['Date of Birth'].values[0] != dob_to_check or
                    existing_record['Also known as'].values[0] != aka_to_check):
                    # Update the corresponding row
                    sheet.loc[sheet['ID'] == id_to_check, ['Date of Birth', 'Also known as']] = dob_to_check, aka_to_check
                    print(f"Record with ID {id_to_check} updated in sheet.")
                return True  # Record was found and updated
    return False  # No matching record found

# Get the first record of cus_dataframe
cus_record = cus_dataframe.iloc[[0]]

# Check if ID exists in any of the sheets, and update or remove as needed
id_exists = match_and_update_or_remove(cus_record, sheets)

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
tools.display_dataframe_to_user(name="Updated Sheet1 After Removal", dataframe=sheet1)
tools.display_dataframe_to_user(name="Updated Sheet2 After Removal", dataframe=sheet2)
tools.display_dataframe_to_user(name="Updated Sheet3 After Removal", dataframe=sheet3)
