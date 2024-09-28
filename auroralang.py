from langchain.llms.base import LLM
from typing import List, Optional

class OraChatLLM(LLM):
    def __init__(self, api_client, model: Optional[str] = None, convo_token: Optional[str] = None):
        # Your ora chat API client
        self.api_client = api_client
        self.model = model
        self.convo_token = convo_token

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # This is where your actual API call happens
        response = self.api_client.chat(msg=prompt, model=self.model, convo_token=self.convo_token)
        return response()['reply']  # Assuming the API returns a dict with 'reply' as the message content

    @property
    def _llm_type(self) -> str:
        return "ora_chat"

# Assuming your API client is set up as `ora_api_client`
ora_llm = OraChatLLM(api_client=ora_api_client)
