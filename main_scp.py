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

# Switch between Plan A (your organization) and Plan B (ora model)
use_plan_b = True  # Set to True for Plan B, False for Plan A

if use_plan_b:
    # Plan B: Use ora model
    result = crawler.run(
        url=url,
        word_count_threshold=1,
        extraction_strategy= CustomLLMExtractionStrategy(
            provider="ora-model",  # ora model
            instruction="Extract information using ora model for processing HTML content."
        ),
        bypass_cache=True,
    )
else:
    # Plan A: Use your organization's model
    result = crawler.run(
        url=url,
        word_count_threshold=1,
        extraction_strategy= CustomLLMExtractionStrategy(
            provider="org-model",  # Your organization's model
            api_token=os.getenv('ORG_MODEL_API_KEY'),
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
