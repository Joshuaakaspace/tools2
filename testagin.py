import os
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from ora import ora  # Importing the ora model connection from ora.py
import json

# Initialize the ORA model connection (Plan B)
ora_connection = ora(auth=os.getenv('ORA_API_KEY'), engine="llama2")

# Define chunking parameters
max_buckets = 12  # Split into a maximum of 12 buckets

# Define the Pydantic model for structuring the extracted data
class ExtractedEntity(BaseModel):
    name: str = Field(..., description="The name of the individual or entity.")
    url: str = Field(None, description="The associated URL, if available.")
    address: str = Field(None, description="The address of the individual or entity, if available.")
    entity_type: str = Field("default", description="Type of the entity, with 'default' as the default value.")
    id_number: bool = Field(True, description="A boolean indicating if the entity has an ID number.")

# Function to split data into buckets based on two empty lines or next row
def split_into_buckets(data: str, max_buckets: int) -> List[str]:
    # Split the data into sections where there are two empty lines
    chunks = data.split("\n\n")
    
    # Limit the number of chunks to max_buckets
    step = max(1, len(chunks) // max_buckets)
    buckets = ['\n\n'.join(chunks[i:i+step]) for i in range(0, len(chunks), step)]
    
    return buckets

# Function to extract entities from a chunk using the LLM
def extract_entities_from_chunk(ix: int, chunk: str, prompt: str) -> List[Dict[str, Any]]:
    print(f"[LOG] Processing chunk {ix}")

    # Send the chunk to the LLM with the specified prompt
    message = f"{prompt}\n{chunk}"
    response = ora_connection.chat(msg=message)

    try:
        extracted_entities = json.loads(response['reply'])  # Parse the JSON response from LLM
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to decode JSON from chunk {ix}")
        return []

    return extracted_entities

# Function to structure the extracted entities using Pydantic
def structure_extracted_data(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    structured_data = []
    
    for entity in entities:
        try:
            # Use Pydantic model to validate and structure the entity
            structured_entity = ExtractedEntity(
                name=entity.get("name", "Unknown"),
                url=entity.get("url", None),
                address=entity.get("address", None),
                entity_type=entity.get("entity_type", "default"),
                id_number=entity.get("id_number", True)
            )
            structured_data.append(structured_entity.dict())  # Convert to dict for JSON serialization
        except Exception as e:
            print(f"Error structuring entity: {e}")
    
    return structured_data

# Function to merge the results from all chunks into a single list
def merge_results(results: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged = []
    for result in results:
        merged.extend(result)
    return merged

# Function to run the extraction process
def run_extraction(data: str, prompt: str) -> List[Dict[str, Any]]:
    # Step 1: Split data into buckets based on two empty lines or next row
    buckets = split_into_buckets(data, max_buckets)
    
    # Step 2: Extract entities from each bucket using the LLM
    extracted_content = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(extract_entities_from_chunk, ix, bucket, prompt) for ix, bucket in enumerate(buckets)]
        
        for future in as_completed(futures):
            try:
                extracted_content.append(future.result())
            except Exception as e:
                print(f"Error in bucket extraction: {e}")
                # Log the error in the results
                extracted_content.append([{"error": True, "message": str(e)}])

    # Step 3: Structure the extracted data using Pydantic
    structured_data = []
    for entities in extracted_content:
        structured_data.extend(structure_extracted_data(entities))

    # Step 4: Merge the results from all buckets
    merged_results = merge_results(structured_data)
    
    print(f"[LOG] Extracted {len(merged_results)} total items.")
    
    return merged_results

# Example data to test with
data_content = """
John Doe
http://example.com/johndoe
1234 Elm St, Anytown, USA
Type: person
ID Number: True

Jane Smith
http://example.com/janesmith
5678 Oak St, Othertown, USA
Type: person
ID Number: False

Some other information here.
"""

# Define the prompt to extract all names and details from each bucket
prompt = """
Extract all individual names, associated URLs, addresses, entity type, and ID number from the text. Return the result as JSON.
"""

# Run the extraction
result = run_extraction(data_content, prompt)

# Output the result as structured JSON
print(json.dumps(result, indent=4))
