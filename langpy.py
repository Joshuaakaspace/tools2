import requests
from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pydantic import BaseModel, Field


class OraChatLLM(LLM, BaseModel):
    """
    Custom LLM class for using the OraChat API.
    """

    api_token: str = Field(..., description="API token for authenticating with OraChat API")
    base_url: str = Field(default='https://api.ora_chat.com/conversation', description="Base URL for the OraChat API")
    model: Optional[str] = Field(default=None, description="Optional model to specify in the API call")
    convo_token: Optional[str] = Field(default=None, description="Optional conversation token to maintain context")

    class Config:
        # This ensures no additional fields can be passed that aren't explicitly defined
        extra = "forbid"

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
