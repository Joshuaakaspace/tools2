import json

# Function to remove entry and return removed record
def remove_entry_and_get_deleted(item, part, df):
    if item is not None:
        if part is not None:
            # Filter and get the row to be deleted
            deleted_row = df[(df['ID'] == item) & (df['Part'] == part)]
            # Remove row from df
            df = df[~((df['ID'] == item) & (df['Part'] == part))]
        else:
            # Filter and get the row to be deleted
            deleted_row = df[df['ID'] == item]
            # Remove row from df
            df = df[df['ID'] != item]
        return df, deleted_row
    return df, None

# Remove the relevant row and extract the deleted record
updated_df, deleted_record = remove_entry_and_get_deleted(item_number, part_number, master_df)

# If a record was deleted, convert it to a JSON structure with "Status: DELETED"
if not deleted_record.empty:
    deleted_record_dict = deleted_record.to_dict(orient='records')[0]
    deleted_record_dict['Status'] = 'DELETED'
    
    # Save the deleted record as a JSON file
    json_file_path = 'deleted_record.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(deleted_record_dict, json_file, indent=4)

# Save the updated DataFrame to a CSV file
updated_df.to_csv('updated_master_df.csv', index=False)

# Display the updated DataFrame
tools.display_dataframe_to_user(name="Updated Master DataFrame", dataframe=updated_df)

# Display the deleted record (if any)
deleted_record_dict if not deleted_record.empty else "No record deleted"
