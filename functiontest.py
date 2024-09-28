# Assuming you have the OraAPIClient class or similar API client defined
# Example: simple function-based approach to use the API client

def initialize_api_client(auth_token: str, engine: str):
    """Initialize and return the API client."""
    # Example of creating the API client. Replace with actual implementation.
    return OraAPIClient(auth=auth_token, engine=engine)


def call_api(api_client, prompt: str, model: Optional[str] = None, convo_token: Optional[str] = None) -> str:
    """Call the API and return the response."""
    # Use the API client to send the prompt and return the reply field from the response
    response = api_client.chat(msg=prompt, model=model, convo_token=convo_token)
    return response.get('reply', '')  # Return the reply, or empty string if not present


# Example usage:

# Initialize the API client
auth_token = "YOUR_AUTH_TOKEN"
engine = "gpt-3"  # or "llama2"
ora_api_client = initialize_api_client(auth_token, engine)

# Example prompt
prompt = "Translate the following text to French: 'Hello, how are you?'"

# Call the API function
response = call_api(ora_api_client, prompt, model="gpt-3")
print(response)
