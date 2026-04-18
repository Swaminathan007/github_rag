from config import Config
from .ollama_handler import OllamaHandler
from .groq_handler import GroqHandler
class LLMUtils:
    def get_llm():
        llm_provider = Config.LLM_PROVIDER
        if(llm_provider.lower() == "ollama"):
            return OllamaHandler()
        elif(llm_provider.lower() == "groq"):
            return GroqHandler()
        else:
            raise ValueError("LLM provider not supported")