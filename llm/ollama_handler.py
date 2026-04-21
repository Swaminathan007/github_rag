from langchain_ollama import ChatOllama, OllamaEmbeddings
from .base import BaseModel
from utils import HttpConnection

class OllamaHandler(BaseModel):
    _provider_name = "ollama"
    def __init__(self):
        super().__init__()
        self.model = self.redis_client.get("ollama_model")
        self.base_url = self.redis_client.get("ollama_base_url")
        self.embedding_model_name = self.redis_client.get("ollama_embedding_model")
        self.embedding_model = self.get_embedding_model()
        self.llm = self.get_llm()

    def get_llm(self):
        if self.llm is None:
            self.llm = ChatOllama(model=self.model, base_url=self.base_url, temperature=0)
        return self.llm

    def get_embedding_model(self):
        if self.embedding_model is None:
            self.embedding_model = OllamaEmbeddings(model=self.embedding_model_name, base_url=self.base_url)
        return self.embedding_model
    def check_health(self):
        try:
            http_client = HttpConnection(self.base_url+"/api/tags")
            http_client.get()
            return http_client.response_code == 200
        except Exception as e:
            print(e)
            return False
    
    @classmethod
    def get_provider_name(cls):
        return cls._provider_name