import os
import math
import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from crawl4ai.extraction_strategy import ExtractionStrategy
from pydantic import BaseModel


class CustomLLMExtractionStrategy(ExtractionStrategy):
    def __init__(self, provider: str = "org-model", api_token: str = None, 
                 instruction: str = None, schema: Dict = None, extraction_type: str = "block", **kwargs):
        super().__init__()
        self.provider = provider
        self.api_token = api_token
        self.instruction = instruction
        self.schema = schema
        self.extract_type = extraction_type
        self.chunk_count = 10  # Number of chunks (buckets) to divide the HTML content into
        self.verbose = kwargs.get("verbose", False)
    
    def _divide_into_buckets(self, html: str, bucket_count: int) -> List[str]:
        """
        Divide the HTML content into equal-sized buckets for individual processing.
        """
        tokens = html.split()  # Split HTML into tokens
        total_tokens = len(tokens)
        tokens_per_bucket = math.ceil(total_tokens / bucket_count)  # Calculate the size of each bucket
        
        buckets = [
            ' '.join(tokens[i:i + tokens_per_bucket])
            for i in range(0, total_tokens, tokens_per_bucket)
        ]
        return buckets

    def extract(self, url: str, ix: int, html: str) -> List[Dict[str, Any]]:
        """
        Extract content from each bucket by sending a POST request to the organization's LLM API.
        """
        print(f"[LOG] Processing bucket {ix} for URL: {url}")
        
        # Prepare the request payload
        payload = {
            "url": url,
            "html": html,
            "instruction": self.instruction,
            "schema": self.schema
        }
        
        # Call the organization's LLM API
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post("https://your-org-model-api.com/v1/extract", json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('blocks', [])
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    def merge_results(self, results: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge the extracted results from all the buckets.
        """
        merged = []
        for result in results:
            merged.extend(result)
        return merged

    def run(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Process the content by dividing it into buckets, processing each individually,
        and merging the results.
        """
        # Divide HTML content into buckets
        buckets = self._divide_into_buckets(html, self.chunk_count)
        
        extracted_content = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.extract, url, ix, bucket) for ix, bucket in enumerate(buckets)]
            
            for future in as_completed(futures):
                try:
                    extracted_content.append(future.result())
                except Exception as e:
                    if self.verbose:
                        print(f"Error in bucket extraction: {e}")
                    # Add error info
                    extracted_content.append([{"error": True, "message": str(e)}])

        # Merge the results from all buckets
        merged_results = self.merge_results(extracted_content)
        
        if self.verbose:
            print(f"[LOG] Extracted {len(merged_results)} total items from URL: {url}")
        
        return merged_results
