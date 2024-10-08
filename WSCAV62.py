import json
from deepdiff import DeepDiff

# Function to load the JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to extract the ID from the 4th field in the object
def get_id_from_object(item):
    return str(item.get('id', None))

# Function to process the differences and generate the required output format
def process_differences(diff, original, updated):
    output = []

    # Handling additions
    if 'dictionary_item_added' in diff:
        for path in diff['dictionary_item_added']:
            id_value = get_id_from_path(path, updated)
            details = get_details_from_path(path, updated)
            output.append({
                'id': id_value,
                'action_type': 'ADDED',
                'details': details
            })

    # Handling deletions
    if 'dictionary_item_removed' in diff:
        for path in diff['dictionary_item_removed']:
            id_value = get_id_from_path(path, original)
            details = get_details_from_path(path, original)
            output.append({
                'id': id_value,
                'action_type': 'DELETED',
                'details': details
            })

    # Handling updates
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            id_value = get_id_from_path(path, original)
            details_before = get_details_from_path(path, original)
            details_after = get_details_from_path(path, updated)
            output.append({
                'id': id_value,
                'action_type': 'UPDATED',
                'details': {
                    'before': details_before,
                    'after': details_after
                }
            })

    return output

# Function to extract the 'id' from a deepdiff path, assuming the 'id' is in the 4th field
def get_id_from_path(path, data):
    # Using the path to locate the correct object in the JSON and get the id from the 4th field
    parts = path.replace("root", "").split("[")
    obj = data
    for part in parts:
        if part:
            key = part.replace("']", "").replace("'", "")
            try:
                obj = obj[int(key)] if key.isdigit() else obj[key]
            except (KeyError, IndexError):
                return None
    # Extract the ID from the 'id' field in the found object
    return get_id_from_object(obj)

# Function to extract details from the object at a deepdiff path
def get_details_from_path(path, data):
    # Using the path to locate the correct object in the JSON (customize this for your path structure)
    parts = path.replace("root", "").split("[")
    obj = data
    for part in parts:
        if part:
            key = part.replace("']", "").replace("'", "")
            try:
                obj = obj[int(key)] if key.isdigit() else obj[key]
            except (KeyError, IndexError):
                return None
    return obj

# Main function to compare two JSON files and save the differences in the required format
def compare_json_files(file1, file2, output_file):
    original = load_json(file1)
    updated = load_json(file2)

    # Extract 'records' from both files
    original_records = original.get("records", [])
    updated_records = updated.get("records", [])

    # Perform a deep diff on 'records'
    diff = DeepDiff(original_records, updated_records, ignore_order=True)

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
