import requests
from typing import Any, List, Optional, Mapping
from pydantic import BaseModel, Field, validator
from langchain_core.language_models.llms import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

# Create a separate Pydantic model for validation
class OraChatLLMConfig(BaseModel):
    api_token: str = Field(..., description="API token for authenticating with OraChat API")
    base_url: str = Field(default='https://api.ora_chat.com/conversation', description="Base URL for the OraChat API")
    model: Optional[str] = Field(default=None, description="Optional model to specify in the API call")
    convo_token: Optional[str] = Field(default=None, description="Optional conversation token to maintain context")

    class Config:
        extra = "forbid"

# Create the LLM class that inherits from LangChain's LLM
class OraChatLLM(LLM):
    """Custom LLM class for using the OraChat API."""

    def __init__(self, api_token: str, base_url: str = 'https://api.ora_chat.com/conversation', model: Optional[str] = None, convo_token: Optional[str] = None):
        """
        Initialize the OraChatLLM with an API token, model, and conversation token.

        This class uses Pydantic to validate the configuration, but does not inherit from it.
        """
        # Use Pydantic model to validate and store configuration
        self.config = OraChatLLMConfig(api_token=api_token, base_url=base_url, model=model, convo_token=convo_token)

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
            "model": self.config.model,  # Optionally use the model if available
            "convo_token": self.config.convo_token,  # Optionally include the conversation token
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }

        # Send the POST request to the OraChat API
        response = requests.post(self.config.base_url, json=payload, headers=headers, verify=False)
        response.raise_for_status()  # Ensure the request was successful

        # Return the 'reply' from the API response
        return response.json().get('reply', '')

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "base_url": self.config.base_url,
            "model": self.config.model,
            "convo_token": self.config.convo_token,
        }
