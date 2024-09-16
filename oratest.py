from typing import Any, Dict, List, Optional, Iterator
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from ora import ora  # Assuming your ora model is imported like this

class CustomChatModelAdvanced(BaseChatModel):
    """
    A custom chat model that interacts with the ORA model using the ora_connection.
    
    Example:

        .. code-block:: python

            model = CustomChatModelAdvanced(model_name="llama2")
            result = model.invoke([HumanMessage(content="hello")])
    """

    model_name: str
    api_token: str
    """The name of the ORA model and the authorization token"""

    def __init__(self, model_name: str, api_token: str):
        self.model_name = model_name
        self.api_token = api_token
        self.ora_connection = ora(auth=self.api_token, engine=self.model_name)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate the response by calling the ORA model using ora_connection.chat().
        
        Args:
            messages: List of messages (prompt).
            stop: Stop tokens.
            run_manager: A run manager with callbacks for the LLM.
        """
        # Extract the content of the last message (prompt)
        last_message = messages[-1].content

        # Call the ORA model using ora_connection
        response = self.ora_connection.chat(msg=last_message)

        # Assuming the ORA model returns a dict with a 'reply' field containing the response
        generated_text = response.get("reply", "")

        # Create the AIMessage with the generated content
        message = AIMessage(
            content=generated_text,
            additional_kwargs={},  # You can add additional metadata if necessary
            response_metadata={"time_in_seconds": 3},  # Example metadata
        )

        # Return the generated message
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """
        Stream the output of the model (if ORA supports streaming).

        Args:
            messages: The prompt as a list of messages.
            stop: Stop tokens.
            run_manager: A run manager with callbacks for the LLM.
        """
        last_message = messages[-1].content

        # Assuming ora_connection has no streaming support; we'll simply yield one chunk with the full response
        response = self.ora_connection.chat(msg=last_message)

        generated_text = response.get("reply", "")

        # Split the response into tokens for streaming (if needed)
        for token in generated_text:
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=token))

            if run_manager:
                run_manager.on_llm_new_token(token, chunk=chunk)

            yield chunk

        # After streaming, add metadata information
        chunk = ChatGenerationChunk(
            message=AIMessageChunk(content="", response_metadata={"time_in_seconds": 3})
        )
        if run_manager:
            run_manager.on_llm_new_token("", chunk=chunk)
        yield chunk

    @property
    def _llm_type(self) -> str:
        """Return the type of language model used by this chat model."""
        return "ora-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": self.model_name,
        }



from langchain_core.messages import HumanMessage

# Initialize the custom ORA model with the token and model name
custom_ora_model = CustomChatModelAdvanced(
    model_name="llama2",
    api_token=os.getenv("ORA_API_KEY")  # Fetch ORA API token from environment variables
)

# Example prompt (using LangChain's HumanMessage)
input_messages = [HumanMessage(content="Explain the process of photosynthesis.")]

# Run the LLM to generate a response
result = custom_ora_model.invoke(input_messages)

# Print the result
print(result.generations[0].message.content)
