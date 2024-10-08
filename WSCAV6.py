import json
from deepdiff import DeepDiff

# Function to load the JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to process the differences and generate the required output format
def process_differences(diff, original, updated):
    output = []

    # Handling additions
    if 'dictionary_item_added' in diff:
        for path in diff['dictionary_item_added']:
            id_value = get_id_from_path(path)
            details = get_details_from_path(path, updated)
            output.append({
                'id': id_value,
                'action_type': 'ADDED',
                'details': details
            })

    # Handling deletions
    if 'dictionary_item_removed' in diff:
        for path in diff['dictionary_item_removed']:
            id_value = get_id_from_path(path)
            details = get_details_from_path(path, original)
            output.append({
                'id': id_value,
                'action_type': 'DELETED',
                'details': details
            })

    # Handling updates
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            id_value = get_id_from_path(path)
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

# Function to extract 'id' from a deepdiff path
def get_id_from_path(path):
    # Assuming id is always present in the path (customize this function for your actual path structure)
    # Example path: "root['data'][1]['id']"
    return path.split("['id']")[0].split('[')[-1].replace("']", "")

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

# Main function to compare two JSON files and print the differences in the required format
def compare_json_files(file1, file2):
    original = load_json(file1)
    updated = load_json(file2)

    # Perform a deep diff
    diff = DeepDiff(original, updated, ignore_order=True)

    # Process the differences and generate output
    output = process_differences(diff, original, updated)

    # Print the output
    for entry in output:
        print(f"id: {entry['id']}, action_type: {entry['action_type']}, details: {entry['details']}")

# Example usage
compare_json_files('file1.json', 'file2.json')
