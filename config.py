# config.py
from typing import Optional

class Config:
    """Class to store configuration settings for the AI Assistant."""
    def __init__(self):
        self.deepinfra_api_key = ""  # DeepInfra API key
        self.api_url = "https://api.deepinfra.com/v1/openai/chat/completions"  # OpenAI-compatible endpoint
        self.serpapi_key = ""  # Replace with your SerpAPI key
        self.serpapi_url = "https://serpapi.com/search"
        self.default_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Default model
        self.fallback_model = "meta-llama/Llama-2-7b-chat-hf"  # Fallback model

    def validate(self) -> bool:
        """Validate that API keys are set."""
        return (self.deepinfra_api_key and "" not in self.deepinfra_api_key and
                self.serpapi_key and "" not in self.serpapi_key)
