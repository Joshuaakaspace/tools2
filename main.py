import os
from crawl4ai import WebCrawler
from pydantic import BaseModel, Field
from custom_llm_extraction_strategy import CustomLLMExtractionStrategy  # Import the custom class

# Define the schema model
class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the OpenAI model.")
    input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
    output_fee: str = Field(..., description="Fee for output token for the OpenAI model.")

# Initialize URL and Crawler
url = 'https://openai.com/api/pricing/'
crawler = WebCrawler()
crawler.warmup()

# Run the extraction with your organization's LLM model
result = crawler.run(
        url=url,
        word_count_threshold=1,
        extraction_strategy= CustomLLMExtractionStrategy(
            provider= "org-model",  # Your organization's model identifier
            api_token = os.getenv('ORG_MODEL_API_KEY'),  # Your organization's API token
            schema=OpenAIModelFee.schema(),
            extraction_type="schema",
            instruction="""From the crawled content, extract all mentioned model names along with their fees for input and output tokens. 
            Do not miss any models in the entire content. One extracted model JSON format should look like this: 
            {"model_name": "GPT-4", "input_fee": "US$10.00 / 1M tokens", "output_fee": "US$30.00 / 1M tokens"}."""
        ),            
        bypass_cache=True,
    )

# Process the final result
print(result)
