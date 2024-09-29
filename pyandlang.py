from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import requests

# Assuming 'ora' is your custom class that interacts with the model API
class OraLLM:
    def __init__(self, auth: str, engine: str):
        if engine == 'llama2':
            self.url = 'https://your-llama2-endpoint-url.com'  # Replace with actual URL
        elif engine == 'gpt-3':
            self.url = 'https://your-gpt3-endpoint-url.com'  # Replace with actual URL
        else:
            raise ValueError("Unsupported engine. Choose either 'llama2' or 'gpt-3'")
        
        self.headers = {'Authorization': f'Bearer {auth}'}

    def chat(self, msg: str, model: Optional[str] = None, convo_token: Optional[str] = None):
        body_json = {"message": msg}
        if convo_token:
            body_json['conversationToken'] = convo_token

        endpoint = f'/conversation?model_name={model}' if model else '/conversation'

        try:
            response = requests.post(
                self.url + endpoint, 
                headers=self.headers, 
                json=body_json, 
                verify=False, 
                timeout=1200
            )
            response.raise_for_status()
            return response.json().get('reply', 'No reply found')
        
        except requests.exceptions.RequestException as e:
            return f"Error occurred: {str(e)}"

# LangChain Custom LLM wrapper for your OraLLM
class CustomOraLLM(LLM):
    def __init__(self, auth: str, engine: str):
        """
        Custom LLM class for using your organization's model via OraLLM.
        
        Parameters:
        - auth: Authorization token for your organization's model.
        - engine: Model engine (e.g., 'llama2' or 'gpt-3').
        """
        super().__init__()
        self.ora_llm = OraLLM(auth=auth, engine=engine)

    @property
    def _llm_type(self) -> str:
        """
        Defines the LLM type for logging purposes.
        """
        return "custom_ora_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        """
        Send the prompt to the custom OraLLM model and return the response.
        
        Parameters:
        - prompt: The prompt to send to the model.
        - stop: (optional) stop tokens not implemented in this example.
        """
        # Call the ora_llm chat function and get the response
        response = self.ora_llm.chat(msg=prompt)

        # You can handle the 'stop' tokens here if necessary
        if stop:
            raise ValueError("Stop kwargs are not permitted.")

        return response

# Example usage
if __name__ == "__main__":
    auth_token = "your_auth_token"  # Replace with your actual auth token
    model_engine = "llama2"  # Or "gpt-3"
    
    # Instantiate the custom LLM with your credentials and engine
    custom_llm = CustomOraLLM(auth=auth_token, engine=model_engine)
    
    # Use it like any other LLM in LangChain
    response = custom_llm("What is the meaning of life?")
    print(response)





from langchain import LLMChain, PromptTemplate

template = "You are a helpful assistant. {question}"
prompt = PromptTemplate(template=template, input_variables=["question"])

# Pass your custom LLM to LLMChain
llm_chain = LLMChain(llm=custom_llm, prompt=prompt)

# Run the chain with an input question
result = llm_chain.run("What is the capital of France?")
print(result)
