import os
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from ora import ora  # Importing the ora model connection from ora.py
import json

# Initialize the ORA model connection (Plan B)
ora_connection = ora(auth=os.getenv('ORA_API_KEY'), engine="llama2")

# Define chunking parameters
chunk_size = 500  # Maximum tokens per chunk
overlap = 0.1  # Overlap rate between chunks (10% by default)

# Define the Pydantic model for structuring the extracted data
class ExtractedEntity(BaseModel):
    name: str = Field(..., description="The name of the individual or entity.")
    url: str = Field(None, description="The associated URL, if available.")
    address: str = Field(None, description="The address of the individual or entity, if available.")
    entity_type: str = Field("default", description="Type of the entity, with 'default' as the default value.")
    id_number: bool = Field(True, description="A boolean indicating if the entity has an ID number.")

# Function to divide the HTML content into chunks with overlap
def divide_with_overlap(html: str, chunk_size: int, overlap: float) -> List[str]:
    tokens = html.split()  # Split content into tokens (words or sub-tokens)
    total_tokens = len(tokens)
    overlap_size = math.ceil(chunk_size * overlap)  # Calculate the overlap size

    # Create chunks with overlap
    chunks = [
        ' '.join(tokens[i:i + chunk_size + overlap_size])
        for i in range(0, total_tokens, chunk_size)
    ]
    return chunks

# Function to extract names and entities from a chunk using the LLM
def extract_entities_from_chunk(ix: int, chunk: str, prompt: str) -> List[Dict[str, Any]]:
    print(f"[LOG] Processing chunk {ix}")

    # Send the chunk to the LLM with the specified prompt
    message = f"{prompt} {chunk}"
    response = ora_connection.chat(msg=message)

    # Assuming response['reply'] contains JSON-like output
    # We expect the LLM to return something like this:
    # [{"name": "John Doe", "url": "http://example.com/johndoe", "address": "1234 Elm St", "entity_type": "person", "id_number": true}]
    
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
def run_extraction(html: str, prompt: str) -> List[Dict[str, Any]]:
    # Step 1: Divide HTML content into chunks with overlap
    chunks = divide_with_overlap(html, chunk_size, overlap)
    
    # Step 2: Extract entities from each chunk using the LLM
    extracted_content = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(extract_entities_from_chunk, ix, chunk, prompt) for ix, chunk in enumerate(chunks)]
        
        for future in as_completed(futures):
            try:
                extracted_content.append(future.result())
            except Exception as e:
                print(f"Error in chunk extraction: {e}")
                # Log the error in the results
                extracted_content.append([{"error": True, "message": str(e)}])

    # Step 3: Structure the extracted data using Pydantic
    structured_data = []
    for entities in extracted_content:
        structured_data.extend(structure_extracted_data(entities))

    # Step 4: Merge the results from all chunks
    merged_results = merge_results(structured_data)
    
    print(f"[LOG] Extracted {len(merged_results)} total items.")
    
    return merged_results

# Example HTML content to test with
html_content = """
This is a large HTML content example with many sentences. 
You can replace this with actual HTML content for testing purposes.
Individuals mentioned: John Doe, Jane Smith, and others.
"""

# Define the prompt to extract all names and details from each chunk
prompt = """
Extract all individual names, associated URLs, addresses, entity type, and ID number from the text. Return the result as JSON.
"""

# Run the extraction
result = run_extraction(html_content, prompt)

# Output the result as structured JSON
print(json.dumps(result, indent=4))
