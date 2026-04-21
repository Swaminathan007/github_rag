from redis_utils import RedisClient
from llm import OllamaHandler,GroqHandler

class LLMUtils:
    
    _active_provider = None
    _active_provider_name = None

    @classmethod
    def get_llm(cls):
        redis_client = RedisClient.get_redis_client()
        provider_name = redis_client.get("llm_provider")

        if not provider_name:
            raise ValueError("LLM provider not set in Redis")

        provider_name = provider_name.lower()

        # Return cached provider if unchanged
        if cls._active_provider and cls._active_provider_name == provider_name:
            print("No change in LLM provider, returning existing provider")
            return cls._active_provider

        # Initialize provider based on value
        if provider_name == OllamaHandler.get_provider_name():
            print("Initializing Ollama provider")
            cls._active_provider = OllamaHandler()

        elif provider_name == GroqHandler.get_provider_name():
            print("Initializing Groq provider")
            cls._active_provider = GroqHandler()

        else:
            raise ValueError(f"LLM provider '{provider_name}' not supported")

        cls._active_provider_name = provider_name
        return cls._active_provider
