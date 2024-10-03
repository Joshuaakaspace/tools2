import json

# Sample JSON data
data = [
    {
        "name": "John Doe",
        "DOB": "1980-01-01",
        "POB": "",
        "position": "Manager",
        "rank": "1",
        "nationality": "American",
        "gender": "Male",
        "passport_number": "",
        "reasons": "Security reasons",
        "date_of_listing": "",
        "other_details": "",
        "address": "123 Main St",
        "also_known_as": ""
    },
    {
        "name": "john doe",
        "dob": "1980-01-01",
        "pob": "New York",
        "position": "Manager",
        "rank": "1",
        "nationality": "",
        "gender": "",
        "passport_number": "A1234567",
        "reasons": "",
        "date_of_listing": "",
        "other_details": "",
        "address": "",
        "also_known_as": "JD"
    }
]

def normalize_fields(record):
    """Convert all field names to lowercase."""
    return {k.lower(): v for k, v in record.items()}

def count_filled_fields(record):
    """Count the number of non-empty fields in a record."""
    return sum(1 for v in record.values() if v)

def remove_empty_or_single_value_records(data):
    """Remove records that are empty or contain only one filled field."""
    return [record for record in data if count_filled_fields(record) > 1]

def merge_similar_records(data):
    """Merge records with similar field values, retaining the record with more filled fields."""
    unique_records = []
    for record in data:
        normalized_record = normalize_fields(record)
        # Try to find an existing similar record
        matched = False
        for unique_record in unique_records:
            if normalized_record['name'] == unique_record['name'] and normalized_record['dob'] == unique_record['dob']:
                # Compare the number of filled fields and keep the one with more details
                if count_filled_fields(normalized_record) > count_filled_fields(unique_record):
                    unique_records.remove(unique_record)
                    unique_records.append(normalized_record)
                matched = True
                break
        if not matched:
            unique_records.append(normalized_record)
    return unique_records

# Step 1: Normalize field names
normalized_data = [normalize_fields(record) for record in data]

# Step 2: Remove empty or single value records
filtered_data = remove_empty_or_single_value_records(normalized_data)

# Step 3: Merge similar records, keeping the one with more details
final_data = merge_similar_records(filtered_data)

# Output the cleaned data
final_data_json = json.dumps(final_data, indent=4)
final_data_json
