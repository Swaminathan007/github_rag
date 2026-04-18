from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from .base import BaseModel
from config import Config
from qdrantutils import QdrantHandler


class GroqHandler(BaseModel):
    def __init__(self):
        super().__init__(Config.GROQ_MODEL,QdrantHandler(Config.QDRANT_URL,Config.QDRANT_API_KEY))
        self.embedding_model_name = Config.OLLAMA_EMBEDDING_MODEL
        self.embedding_model = self.get_embedding_model()
        self.api_key = Config.GROQ_API_KEY
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
            print(e)
            return False