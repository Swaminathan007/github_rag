# llm/ollama_handler.py
from langchain_ollama import ChatOllama, OllamaEmbeddings
from .base import BaseModel
from config import Config
from utils import HttpConnection
from qdrantutils import QdrantHandler

class OllamaHandler(BaseModel):
    def __init__(self):
        super().__init__(Config.OLLAMA_MODEL,QdrantHandler(Config.QDRANT_URL,Config.QDRANT_API_KEY))
        self.base_url = Config.OLLAMA_BASE_URL
        self.embedding_model_name = Config.OLLAMA_EMBEDDING_MODEL
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