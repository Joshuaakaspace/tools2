from typing import Any, Dict, Iterator, List, Optional
from pydantic import BaseModel, Field
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

class OraChatLLM(LLM, BaseModel):
    """A custom chat model that integrates with the OraAPIClient."""

    api_client: Any = Field(...)
    model: Optional[str] = Field(default=None)
    convo_token: Optional[str] = Field(default=None)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the OraAPIClient on the given input and return the response."""
        # Make the API call via api_client.chat method
        response = self.api_client.chat(msg=prompt, model=self.model, convo_token=self.convo_token)
        
        # Assuming the response contains a 'reply' field
        return response.get('reply', '')

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the OraAPIClient on the given prompt (if supported)."""
        response = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
        for char in response:
            chunk = GenerationChunk(text=char)
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": "OraChatModel",
            "model": self.model,
            "convo_token": self.convo_token,
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "ora_chat"
