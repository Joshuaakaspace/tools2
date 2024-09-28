from typing import Optional, List, Any
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk


class OraChatLLM(LLM):
    """Custom LLM wrapper for OraChat API"""

    def __init__(self, api_client, model: Optional[str] = None, convo_token: Optional[str] = None):
        """Initialize the OraChatLLM with an API client, model, and conversation token."""
        self.api_client = api_client
        self.model = model
        self.convo_token = convo_token

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Send a prompt to the API and return the response."""
        response = self.api_client.chat(msg=prompt, model=self.model, convo_token=self.convo_token)
        
        # Return the 'reply' field from the response
        return response.get('reply', '')

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream tokens from the OraChat API (if supported)."""
        response = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
        
        # Simulate streaming by yielding each character (adjust for actual token-based streaming if possible)
        for char in response:
            chunk = GenerationChunk(text=char)
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk

    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "ora_chat"

    @property
    def _identifying_params(self) -> dict:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": "OraChatLLM",
            "model": self.model,
        }
