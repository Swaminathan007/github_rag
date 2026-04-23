from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from .base import BaseModel

class GroqHandler(BaseModel):
    _provider_name = "groq"
    def __init__(self):
        super().__init__()
        self.model = self.redis_client.get("groq_model")
        self.embedding_model_name = self.redis_client.get("groq_embedding_model")
        self.embedding_model = self.get_embedding_model()
        self.api_key = self.redis_client.get("groq_api_key")
        self.llm = self.get_llm()
    
    def get_llm(self):
        if self.llm is None:
            self.llm = ChatGroq(model=self.model, temperature=0,api_key=self.api_key)
        return self.llm
    
    def get_embedding_model(self):
        if self.embedding_model is None:
            self.embedding_model = OllamaEmbeddings(model=self.embedding_model_name,)
        return self.embedding_model

    def check_health(self):
        try:
            self.llm.invoke("Hello")
            return True
        except Exception as e:
            self.__logger.error(e)
            return False
    
    @classmethod
    def get_provider_name(cls):
        return cls._provider_name