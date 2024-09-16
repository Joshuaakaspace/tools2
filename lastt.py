import requests
from typing import Optional, List, Any
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

class LLMWrapper(LLM):
    """
    Custom LLM class for integrating with a custom API and supporting callback management.
    """
    api_url: str
    headers: dict

    def __init__(self, api_url: str, headers: dict, **kwargs):
        """
        Initialize the LLMWrapper with the API URL and headers, and ensure the parent class is initialized correctly.
        """
        super().__init__(**kwargs)  # Initialize the parent class to avoid issues with Pydantic
        self.api_url = api_url
        self.headers = headers

    @property
    def _llm_type(self) -> str:
        """
        Return the type of the LLM, identifying it as a custom LLM.
        """
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None
    ) -> str:
        """
        Make an API call to the custom LLM using the provided prompt, managing callbacks.
        """

        # Ensure that stop sequences are not used, as per your model's design
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        # Optional: Handle the start of the run if a callback manager is provided
        if run_manager:
            run_manager.on_llm_start(serialized={"name": "custom_llm"}, prompts=[prompt])

        try:
            # Make the API request
            response = requests.post(
                self.api_url,
                json={
                    "on_behalf_of_client": "",
                    "on_behalf_of_user": "",
                    "query": prompt,
                    "ai_agent": "CREATIVE AGENT",  # Modify the AI agent as needed
                    "stream": False,
                    "debug": False
                },
                headers=self.headers
            )

            # Check if the response is successful
            if response.status_code == 200:
                # Parse the answer from the API response
                answer = response.json().get('answer')

                # Handle the end of the run if a callback manager is provided
                if run_manager:
                    run_manager.on_llm_end({"generations": [{"text": answer}]})

                return str(answer)
            else:
                # Raise an exception if the request fails
                raise Exception(f"Failed to get a response from the API. Status code: {response.status_code}")

        except Exception as e:
            # Handle any errors if a callback manager is provided
            if run_manager:
                run_manager.on_llm_error(e)
            raise e


# Example usage:

# Define the API URL and headers (with your API token or credentials)
api_url = "YOUR_API_URL_HERE"
api_token = "YOUR_API_TOKEN_HERE"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Instantiate the LLMWrapper with the custom API
llm = LLMWrapper(api_url, headers)

# Example of calling the model with a prompt
response = llm._call("Your prompt here", run_manager=CallbackManagerForLLMRun())
print(response)
