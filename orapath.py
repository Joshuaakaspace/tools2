import requests

class OraAPIClient:
    def __init__(self, auth: str, engine: str):
        # Set the URL based on the engine
        if engine == 'llama2':
            self.url = 'https://llama2-api-url.com'
        elif engine == 'gpt-3':
            self.url = 'https://gpt-3-api-url.com'
        else:
            raise ValueError("Unsupported engine! Use 'llama2' or 'gpt-3'.")

        # Authorization headers
        self.headers = {'Authorization': f'Bearer {auth}'}

    def chat(self, msg: str, model: str = None, convo_token: str = None, echo: bool = False):
        # Prepare the body JSON for the POST request
        body_json = {"message": msg}

        if convo_token:
            body_json['conversationToken'] = convo_token

        if model:
            endpoint = f'/conversation?model_name={model}'
        else:
            endpoint = '/conversation'  # Default endpoint without model

        # Make the POST request
        response = requests.post(self.url + endpoint, headers=self.headers, json=body_json, verify=False, timeout=1200)

        # Print the reply if echo is True
        if echo:
            print(response.json()['reply'])
            print(response.status_code, "\n__________________________________")

        return response.json()  # Return the full JSON response
