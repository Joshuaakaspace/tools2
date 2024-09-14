from pydantic import BaseModel, ValidationError
from typing import List

# Split data based on two empty lines
def split_data(data: str, num_buckets: int):
    sections = data.split("\n\n")
    bucket_size = max(1, len(sections) // num_buckets)
    buckets = [sections[i:i + bucket_size] for i in range(0, len(sections), bucket_size)]
    return buckets

# Create prompt for LLM
def create_prompt(bucket_data):
    prompt = "Extract the following fields from the data into JSON format: name, case_number, details.\n\n"
    prompt += "\n".join(bucket_data)
    return prompt

# Pydantic Model for validation
class ExtractedData(BaseModel):
    name: str
    case_number: str
    details: str

# Validate extracted JSON data
def validate_extracted_data(extracted_json: List[dict]):
    valid_data = []
    for entry in extracted_json:
        try:
            validated = ExtractedData(**entry)
            valid_data.append(validated.dict())
        except ValidationError as e:
            print(f"Validation error for entry: {entry}. Error: {e}")
    return valid_data

# Merge all the extracted JSON from different buckets
def merge_extracted_json(bucketed_extracted_data: List[List[dict]]):
    merged_data = []
    for bucket_data in bucketed_extracted_data:
        merged_data.extend(validate_extracted_data(bucket_data))
    return merged_data

# Example Usage
if __name__ == "__main__":
    # Simulate some large text data
    data = """name: John Doe
case_number: 12345
details: Some details here.

name: Jane Smith
case_number: 67890
details: Other details here.

name: Someone Else
case_number: 11121
details: Different details."""

    # Split data into 10 buckets
    buckets = split_data(data, 10)

    # Simulate extracted JSON from each bucket (normally this would come from the LLM)
    bucketed_extracted_json = [
        [
            {"name": "John Doe", "case_number": "12345", "details": "Some details here."},
            {"name": "Jane Smith", "case_number": "67890", "details": "Other details here."}
        ],
        [
            {"name": "Someone Else", "case_number": "11121", "details": "Different details"}
        ]
    ]

    # Merge all the extracted JSON from different buckets
    merged_json = merge_extracted_json(bucketed_extracted_json)
    print(f"Merged JSON Data: {merged_json}")
