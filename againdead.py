import json
from deepdiff import DeepDiff

# Function to load the JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to create a unique identifier by concatenating 'id', 'part', and 'schedule'
def create_unique_identifier(record):
    id_part = str(record.get('id', ''))
    part = str(record.get('part', ''))
    schedule = str(record.get('schedule', ''))
    return f"{id_part}_{part}_{schedule}"

# Function to add a unique identifier to each record in the list of records
def add_unique_identifier(records):
    for record in records:
        record['_unique_id'] = create_unique_identifier(record)
    return records

# Helper function to extract a value from a path
def extract_value_from_path(path, data):
    obj = data
    for key in path:
        if isinstance(key, str) and key.startswith('root'):
            continue  # Ignore the root part of the path
        try:
            obj = obj[int(key)] if isinstance(key, int) else obj[key]
        except (KeyError, IndexError):
            return None
    return obj

# Function to process the differences and generate the required output format
def process_differences(diff, original_records, updated_records):
    output = {
        "added": [],
        "deleted": [],
        "updated": []
    }

    # Handling additions (new records)
    if 'dictionary_item_added' in diff:
        for path in diff['dictionary_item_added']:
            added_item = extract_value_from_path(path, updated_records)
            if added_item:
                id_value = added_item.get('_unique_id')
                output['added'].append({
                    'id': id_value,
                    'details': added_item
                })

    # Handling deletions (removed records)
    if 'dictionary_item_removed' in diff:
        for path in diff['dictionary_item_removed']:
            removed_item = extract_value_from_path(path, original_records)
            if removed_item:
                id_value = removed_item.get('_unique_id')
                output['deleted'].append({
                    'id': id_value,
                    'details': removed_item
                })

    # Handling updates (changed values within existing records)
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            id_value = path[0]  # The first element in the path tuple is the record identifier
            details_before = change['old_value']
            details_after = change['new_value']
            output['updated'].append({
                'id': id_value,
                'details': {
                    'before': details_before,
                    'after': details_after
                }
            })

    return output

# Main function to compare two JSON files and save the differences in the required format
def compare_json_files(file1, file2, output_file):
    original = load_json(file1)
    updated = load_json(file2)

    # Extract 'records' from both files
    original_records = original.get("records", [])
    updated_records = updated.get("records", [])

    # Add a unique identifier to each record in the original and updated files
    original_records = add_unique_identifier(original_records)
    updated_records = add_unique_identifier(updated_records)

    # Perform a deep diff on the records without converting to an index-based dictionary
    diff = DeepDiff(original_records, updated_records, ignore_order=True)

    # Process the differences and generate output
    output = process_differences(diff, original_records, updated_records)

    # Save the output to a file
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=4)

    print(f"Differences saved to {output_file}")

    return output_file

# Example usage
file1_path = '/mnt/data/file1.json'
file2_path = '/mnt/data/file2.json'
output_file_path = '/mnt/data/final_output_differences_with_unique_id.json'

# Compare the files and save the delta output
compare_json_files(file1_path, file2_path, output_file_path)

# Returning the path of the delta output file
output_file_path
