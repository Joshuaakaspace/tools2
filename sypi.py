from langchain.chat_models.base import BaseChatModel
from typing import List
from langchain.schema import ChatResult, HumanMessage, AIMessage, SystemMessage

class MyCustomChatModel(BaseChatModel):
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def _call_api(self, prompt: str) -> str:
        # Example of calling your own API
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        json_data = {
            "prompt": prompt
        }
        response = requests.post(self.api_url, headers=headers, json=json_data)
        result = response.json()
        return result["response"]

    def _generate(self, messages: List[HumanMessage], **kwargs) -> ChatResult:
        # Convert the list of messages into a single prompt
        prompt = "\n".join([message.content for message in messages if isinstance(message, HumanMessage)])

        # Call the custom model API with the prompt
        response = self._call_api(prompt)
        
        # Return a LangChain ChatResult (you may need to modify it to match your response)
        return ChatResult(
            generations=[AIMessage(content=response)],
            llm_output={"token_usage": 0}  # You can add any additional model output data here
        )

    @property
    def _llm_type(self) -> str:
        return "my-custom-chat-model"

my_chat_model = MyCustomChatModel(
    api_url="https://my-custom-model-api.com/v1/chat",
    api_key="your-api-key"
)

# Use your custom model just like you'd use ChatOpenAI
response = my_chat_model._generate([HumanMessage(content="Hello, how are you?")])

print(response.generations[0].content)


from langchain.agents import initialize_agent, ToolType
from langchain.tools import Tool

# Your API tool, for example
weather_tool = Tool(
    name="Get Weather",
    func=get_weather,
    description="Use this tool to get the current weather for a location."
)

# Initialize the agent with your custom chat model and tools
tools = [weather_tool]
agent = initialize_agent(
    tools=tools, 
    llm=my_chat_model,  # Use your custom chat model here
    agent_type=ToolType.ZERO_SHOT_REACT_DESCRIPTION
)

# Run the agent
response = agent.run("What’s the weather in Paris?")
print(response)


    def _generate(self, messages: List[HumanMessage], **kwargs) -> ChatResult:
        # Collect previous conversation and current prompt
        conversation_history = "\n".join([message.content for message in messages])

        # Call the custom model API with the conversation history
        response = self._call_api(conversation_history)

        # Return the response as a ChatResult
        return ChatResult(
            generations=[AIMessage(content=response)]
        )

