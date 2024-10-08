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

# Function to convert records to an index-based dictionary using the unique identifier
def convert_to_index_oriented_with_unique_id(records):
    index_oriented = {}
    for record in records:
        unique_id = create_unique_identifier(record)
        if unique_id:
            index_oriented[unique_id] = record  # Use unique ID as key
    return index_oriented

# Function to process the differences and generate the required output format
def process_differences(diff, original, updated):
    output = {
        "added": [],
        "deleted": [],
        "updated": []
    }

    # Handling additions (new records)
    if 'dictionary_item_added' in diff:
        for path, added_item in diff['dictionary_item_added'].items():
            id_value = create_unique_identifier(added_item)
            if id_value:
                output['added'].append({
                    'id': id_value,
                    'details': added_item
                })

    # Handling deletions (removed records)
    if 'dictionary_item_removed' in diff:
        for path, removed_item in diff['dictionary_item_removed'].items():
            id_value = create_unique_identifier(removed_item)
            if id_value:
                output['deleted'].append({
                    'id': id_value,
                    'details': removed_item
                })

    # Handling updates (changed values within existing records)
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            # Extract unique identifier for the record
            id_value = path[0]  # The first element in the path tuple is the unique identifier
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

    # Convert records to an index-based dictionary using the unique identifier
    original_indexed = convert_to_index_oriented_with_unique_id(original_records)
    updated_indexed = convert_to_index_oriented_with_unique_id(updated_records)

    # Perform a deep diff on the index-oriented records
    diff = DeepDiff(original_indexed, updated_indexed, ignore_order=True)

    # Process the differences and generate output
    output = process_differences(diff, original_indexed, updated_indexed)

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
