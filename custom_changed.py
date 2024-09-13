import os
import math
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from ora import ora  # Importing the ora model connection from ora.py

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

# Function to extract content for a single chunk using the ora model
def extract_chunk(ix: int, chunk: str) -> Dict[str, Any]:
    print(f"[LOG] Processing chunk {ix}")
    
    # Use ora's chat model for extraction
    response = ora_connection.chat(msg=chunk)
    
    print(f"[LOG] Response from ora model for chunk {ix}: {response['reply']}")
    
    # Return structured JSON output for this chunk using Pydantic
    extracted_entity = ExtractedEntity(
        name="John Doe",  # Replace with actual parsing logic from the response
        url="http://example.com",
        address="1234 Main St",
        entity_type="person",
        id_number=True
    )
    
    return {"chunk": ix, "data": extracted_entity.dict()}

# Function to merge extracted results from all chunks into a structured list
def merge_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = []
    for result in results:
        merged.append(result)
    return merged

# Function to run the extraction process
def run_extraction(html: str) -> List[Dict[str, Any]]:
    # Step 1: Divide HTML content into chunks with overlap
    chunks = divide_with_overlap(html, chunk_size, overlap)
    
    # Step 2: Process each chunk in parallel
    extracted_content = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(extract_chunk, ix, chunk) for ix, chunk in enumerate(chunks)]
        
        for future in as_completed(futures):
            try:
                extracted_content.append(future.result())
            except Exception as e:
                print(f"Error in chunk extraction: {e}")
                # Log the error in the results
                extracted_content.append({"error": True, "message": str(e)})

    # Step 3: Merge the results from all chunks
    merged_results = merge_results(extracted_content)
    
    print(f"[LOG] Extracted {len(merged_results)} total items.")
    
    return merged_results

# Example HTML content to test with
html_content = """
This is a large HTML content example with many sentences. 
You can replace this with actual HTML content for testing purposes.
Model GPT-4 costs US$10.00 for input tokens and US$30.00 for output tokens.
"""

# Run the extraction
result = run_extraction(html_content)

# Output the result as structured JSON
import json
print(json.dumps(result, indent=4))
