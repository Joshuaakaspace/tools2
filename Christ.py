from pydantic import BaseModel, ValidationError
from typing import List, Union
from ora import ora  # Assuming you have already installed and set up the ora library

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
            # Check if entry is a dictionary
            if isinstance(entry, dict):
                validated = ExtractedData(**entry)
                valid_data.append(validated.dict())
            else:
                print(f"Invalid entry format (expected dict): {entry}")
        except ValidationError as e:
            print(f"Validation error for entry: {entry}. Error: {e}")
    return valid_data

# Call LLM for each bucket
def extract_data_from_llm(bucket_data):
    prompt = create_prompt(bucket_data)
    # Call LLM with the generated prompt
    response = ora.chat(msg=prompt)
    
    # Assuming the response is already a dictionary or list of dictionaries
    if isinstance(response, list):
        return response
    elif isinstance(response, dict):
        return [response]
    else:
        print(f"Unexpected LLM response format: {response}")
        return []

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
    
    # List to hold all bucketed extracted data
    bucketed_extracted_json = []
    
    # Process each bucket through LLM and extract data
    for bucket in buckets:
        extracted_json = extract_data_from_llm(bucket)
        bucketed_extracted_json.append(extracted_json)
    
    # Merge all the extracted JSON from different buckets
    merged_json = merge_extracted_json(bucketed_extracted_json)
    print(f"Merged JSON Data: {merged_json}")