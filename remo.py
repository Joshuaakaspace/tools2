def remove_matching_record(cus_record, sheets):
    """
    This function checks if the given cus_record matches any record in the provided sheets.
    If a matching record is found (ID, Name, Date of Birth, Also known as are identical), it removes that record from the sheet.
    
    :param cus_record: The record (dataframe row) to check.
    :param sheets: List of dataframes (sheets) to check against.
    :return: None
    """
    id_to_check = cus_record['ID'].values[0]
    name_to_check = cus_record['Name'].values[0]
    dob_to_check = cus_record['Date of Birth'].values[0]
    aka_to_check = cus_record['Also known as'].values[0]
    
    for sheet in sheets:
        # Check if the ID exists in the sheet
        existing_record = sheet[sheet['ID'] == id_to_check]
        if not existing_record.empty:
            # Check if all fields match
            if (existing_record['Name'].values[0] == name_to_check and
                existing_record['Date of Birth'].values[0] == dob_to_check and
                existing_record['Also known as'].values[0] == aka_to_check):
                # If all fields match, remove the record
                sheet.drop(sheet[sheet['ID'] == id_to_check].index, inplace=True)
                print(f"Record with ID {id_to_check} removed from sheet.")
                return True  # Record was found and removed
    return False  # No matching record found
