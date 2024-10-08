import json
from deepdiff import DeepDiff

# Function to load the JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to reorder the fields in the records so that 'id' comes first
def reorder_record_fields(records):
    reordered_records = []
    for record in records:
        if 'id' in record:
            # Create a new dictionary with 'id' as the first field, followed by the rest
            reordered_record = {k: record[k] for k in ['id'] if k in record}
            reordered_record.update({k: record[k] for k in record if k != 'id'})
            reordered_records.append(reordered_record)
    # Sort the records by 'id' for consistent delta comparison
    reordered_records.sort(key=lambda x: x['id'])
    return reordered_records

# Function to process the differences and generate the required output format
def process_differences(diff, original, updated):
    output = []

    print("Processing differences...")

    # Handling additions (new records)
    if 'iterable_item_added' in diff:
        for path, added_item in diff['iterable_item_added'].items():
            id_value = added_item.get('id')
            if id_value:
                output.append({
                    'id': id_value,
                    'action_type': 'ADDED',
                    'details': added_item
                })

    # Handling deletions (removed records)
    if 'iterable_item_removed' in diff:
        for path, removed_item in diff['iterable_item_removed'].items():
            id_value = removed_item.get('id')
            if id_value:
                output.append({
                    'id': id_value,
                    'action_type': 'DELETED',
                    'details': removed_item
                })

    # Handling updates (changed values within existing records)
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            # Extract id from the original and updated records
            id_value = get_id_from_path(path, original)
            details_before = get_details_from_path(path, original)
            details_after = get_details_from_path(path, updated)
            if id_value:
                output.append({
                    'id': id_value,
                    'action_type': 'UPDATED',
                    'details': {
                        'before': details_before,
                        'after': details_after
                    }
                })

    print("Processed differences output: ", output)  # Debugging output
    return output

# Function to extract the 'id' from a deepdiff path (handling path as tuple)
def get_id_from_path(path, data):
    obj = data
    for key in path:
        try:
            obj = obj[key]  # Navigate using the tuple elements (key or index)
        except (KeyError, IndexError, TypeError):
            return None
    return obj.get('id')

# Function to extract details from the object at a deepdiff path (handling path as tuple)
def get_details_from_path(path, data):
    obj = data
    for key in path:
        try:
            obj = obj[key]  # Navigate using the tuple elements (key or index)
        except (KeyError, IndexError, TypeError):
            return None
    return obj

# Main function to compare two JSON files and save the differences in the required format
def compare_json_files(file1, file2, output_file):
    original = load_json(file1)
    updated = load_json(file2)

    # Extract 'records' from both files
    original_records = original.get("records", [])
    updated_records = updated.get("records", [])

    # Reorder records so that 'id' is the first field and sort by 'id'
    original_records = reorder_record_fields(original_records)
    updated_records = reorder_record_fields(updated_records)

    # Perform a deep diff on 'records'
    diff = DeepDiff(original_records, updated_records, ignore_order=True)

    print("DeepDiff result: ", diff)  # Debugging output

    # Process the differences and generate output
    output = process_differences(diff, original_records, updated_records)

    # Save the output to a file
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=4)

    return output_file

# Example usage
file1_path = '/mnt/data/file1.json'
file2_path = '/mnt/data/file2.json'
output_file_path = '/mnt/data/delta_output_with_records.json'

# Compare the files and save the delta output
compare_json_files(file1_path, file2_path, output_file_path)

# Returning the path of the delta output file
output_file_path
