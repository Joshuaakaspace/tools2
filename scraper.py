from typing import List
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

# Manual Validation of Extracted Data
def validate_extracted_data(extracted_json: List[dict]):
    valid_data = []
    required_keys = {"name", "case_number", "details"}
    
    for entry in extracted_json:
        # Ensure entry is a dictionary and contains the required keys
        if isinstance(entry, dict) and required_keys.issubset(entry.keys()):
            valid_data.append(entry)
        else:
            print(f"Invalid or incomplete entry: {entry}")
    return valid_data

# Call LLM for each bucket and add bucket index to the extracted data
def extract_data_from_llm(bucket_data, bucket_index):
    prompt = create_prompt(bucket_data)
    # Call LLM with the generated prompt
    response = ora.chat(msg=prompt)
    
    # Assuming the response is a list of dictionaries (the extracted data)
    if isinstance(response, list):
        # Add a "bucket_index" field to each extracted entry
        for entry in response:
            if isinstance(entry, dict):  # Ensure it's a dictionary before adding the field
                entry['bucket_index'] = bucket_index
        return response
    elif isinstance(response, dict):
        # If response is a single dict, wrap it in a list and add the bucket index
        response['bucket_index'] = bucket_index
        return [response]
    else:
        print(f"Unexpected LLM response format: {response}")
        return []

# Refine the data by sending it back with original bucket data
def refine_data_with_llm(bucket_data, extracted_data):
    prompt = f"Refine the extraction based on the following data and correct any mistakes:\n\nOriginal Data:\n{bucket_data}\n\nExtracted Data:\n{extracted_data}"
    response = ora.chat(msg=prompt)
    
    # Assuming the response is a refined version of the extracted data
    if isinstance(response, list):
        return response
    elif isinstance(response, dict):
        return [response]
    else:
        print(f"Unexpected LLM response format during refinement: {response}")
        return []

# Merge all the extracted JSON from different buckets
def merge_extracted_json(bucketed_extracted_data: List[List[dict]]):
    merged_data = []
    for bucket_data in bucketed_extracted_data:
        merged_data.extend(validate_extracted_data(bucket_data))
    return merged_data

# Calculate score based on completeness of extracted fields
def calculate_completeness_score(refined_extracted_json: List[dict]):
    required_keys = {"name", "case_number", "details"}
    total_score = 0
    max_score_per_entry = len(required_keys)  # Max score per entry (3 fields)
    
    # Track scores for each entry
    entry_scores = []

    for entry in refined_extracted_json:
        # Calculate the score for each entry
        entry_score = sum(1 for key in required_keys if key in entry and entry[key])  # 1 point for each present field
        total_score += entry_score
        entry_scores.append({"entry": entry, "score": entry_score, "max_score": max_score_per_entry})
    
    # Overall percentage score
    total_possible_score = len(refined_extracted_json) * max_score_per_entry
    overall_score_percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0

    return entry_scores, overall_score_percentage

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
    for index, bucket in enumerate(buckets):
        extracted_json = extract_data_from_llm(bucket, index)  # Pass the bucket index
        # Refine the extracted data by sending it back with original data
        refined_extracted_json = refine_data_with_llm(bucket, extracted_json)
        
        # Append the refined extracted data to the bucketed data list
        bucketed_extracted_json.append(refined_extracted_json)
    
    # Merge all the extracted JSON from different buckets
    merged_json = merge_extracted_json(bucketed_extracted_json)
    
    # Calculate the completeness score
    entry_scores, overall_score_percentage = calculate_completeness_score(merged_json)
    
    # Display the results
    print(f"Entry Scores: {entry_scores}")
    print(f"Overall Score Percentage: {overall_score_percentage:.2f}%")
