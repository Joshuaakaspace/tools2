from typing import Any, AsyncIterator, Dict, Iterator, List, Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import run_in_executor
import requests  # Assuming we are using an API for the custom LLM

class CustomChatModelAdvanced(BaseChatModel):
    """
    A custom chat model that interacts with a custom LLM model API.
    
    Example:
    
        .. code-block:: python
    
            model = CustomChatModelAdvanced(model_name="custom-model", api_url="https://api.custom-llm.com")
            result = model.invoke([HumanMessage(content="hello")])
    """
    
    model_name: str
    api_url: str
    """The URL for the custom LLM API."""
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Override the _generate method to implement the custom chat model logic.
        
        This will call the custom LLM API with the message and retrieve the response.
        
        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
            run_manager: A run manager with callbacks for the LLM.
        """
        # Get the content of the last message to send to the custom LLM API
        last_message = messages[-1].content

        # Prepare the request payload (assuming the custom LLM accepts a simple JSON structure)
        payload = {
            "model": self.model_name,
            "prompt": last_message,
            "stop": stop
        }

        # Make a POST request to the custom LLM API
        response = requests.post(self.api_url, json=payload)

        if response.status_code == 200:
            # Assuming the API response contains a 'text' field with the LLM response
            response_data = response.json()
            generated_text = response_data.get("text", "")
        else:
            raise Exception(f"API call failed with status code {response.status_code}")

        # Create the AIMessage with the generated content
        message = AIMessage(
            content=generated_text,
            additional_kwargs={},  # Add additional metadata if needed
            response_metadata={"time_in_seconds": 3},  # Example metadata
        )

        # Return the generated result in the required format
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
        Stream the output of the model.

        If the custom LLM model supports streaming, implement that logic here.
        Otherwise, the generation will use the _generate method.
        
        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
            run_manager: A run manager with callbacks for the LLM.
        """
        # Get the content of the last message
        last_message = messages[-1].content

        # Prepare the request payload (assuming the LLM supports streaming)
        payload = {
            "model": self.model_name,
            "prompt": last_message,
            "stop": stop
        }

        # Make a streaming request to the custom LLM API
        with requests.post(self.api_url + "/stream", json=payload, stream=True) as response:
            if response.status_code == 200:
                # Stream the tokens from the LLM response
                for chunk in response.iter_lines():
                    token = chunk.decode('utf-8')
                    ai_chunk = AIMessageChunk(content=token)
                    
                    # Handle callbacks if available
                    if run_manager:
                        run_manager.on_llm_new_token(token, chunk=ai_chunk)

                    yield ChatGenerationChunk(message=ai_chunk)
            else:
                raise Exception(f"Streaming API call failed with status code {response.status_code}")

        # Add metadata after streaming is done
        chunk = ChatGenerationChunk(
            message=AIMessageChunk(content="", response_metadata={"time_in_seconds": 3})
        )
        if run_manager:
            run_manager.on_llm_new_token("", chunk=chunk)
        yield chunk

    @property
    def _llm_type(self) -> str:
        """Return the type of language model used by this chat model."""
        return "custom-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": self.model_name,
        }



from langchain_core.prompts import PromptTemplate
from langchain_core.chains import LLMChain

# Assume you have already defined your `CustomChatModelAdvanced` class above.

# Step 1: Define the custom LLM model
custom_llm = CustomChatModelAdvanced(
    model_name="custom-model",
    api_url="https://api.custom-llm.com"  # Replace with your custom LLM API URL
)

# Step 2: Define a prompt template
prompt_template = PromptTemplate(
    input_variables=["input_text"],  # This allows you to pass dynamic content into the prompt
    template="""
    You are an intelligent assistant. Here is the user's input:
    {input_text}
    Please respond in a detailed and informative manner.
    """
)

# Step 3: Create an LLMChain
llm_chain = LLMChain(
    llm=custom_llm,  # Pass your custom model here
    prompt=prompt_template
)

# Step 4: Run the chain with an input
input_text = "Explain the process of photosynthesis."

# The chain will run the input through your custom model and generate a response
response = llm_chain.run(input_text)

# Output the response
print(response)
