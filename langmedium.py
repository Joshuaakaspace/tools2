import requests
from typing import Any, List, Optional, Mapping
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM


class OraChatLLM(LLM):
    """
    Custom LLM class for using the OraChat API.
    """
    
    api_token: str
    base_url: str
    model: Optional[str] = None
    convo_token: Optional[str] = None

    def __init__(self, api_token: str, base_url: str = 'https://api.ora_chat.com/conversation', model: Optional[str] = None, convo_token: Optional[str] = None):
        """
        Initialize the OraChatLLM with an API token, model, and conversation token.
        """
        self.api_token = api_token
        self.base_url = base_url
        self.model = model
        self.convo_token = convo_token

    @property
    def _llm_type(self) -> str:
        """Return the LLM type, used for logging."""
        return "ora_chat"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Make an API call to OraChat using the specified prompt and return the response.
        """
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        # Define the payload for the API call
        payload = {
            "message": prompt,
            "model": self.model,  # Optionally use the model if available
            "convo_token": self.convo_token,  # Optionally include the conversation token
        }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Send the POST request to the OraChat API
        response = requests.post(self.base_url, json=payload, headers=headers, verify=False)
        response.raise_for_status()  # Ensure the request was successful

        # Return the 'reply' from the API response
        return response.json().get('reply', '')

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "base_url": self.base_url,
            "model": self.model,
            "convo_token": self.convo_token,
        }

# Example Usage
api_token = "YOUR_API_TOKEN"
ora_llm = OraChatLLM(api_token=api_token, model="gpt-3")

# Testing with LangChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Define a prompt template
prompt_template = PromptTemplate.from_template("Translate the following text to French: {text}")

# Create the chain using your custom LLM
chain = LLMChain(llm=ora_llm, prompt=prompt_template)

# Run the chain with some input
output = chain.run(text="Hello, how are you?")
print(output)
