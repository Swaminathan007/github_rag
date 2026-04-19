from abc import ABC, abstractmethod
from qdrantutils import QdrantHandler
from redis_utils import RedisClient
from config import Config

class BaseModel(ABC):
    def __init__(self):
        self.model = None
        self.embedding_model_name = None
        self.embedding_model = None
        self.llm = None
        self.vector_db = QdrantHandler(Config.QDRANT_URL,Config.QDRANT_API_KEY)
        self.context = None
        self.redis_client = RedisClient.get_redis_client()

    # -------- ABSTRACT METHODS --------
    @abstractmethod
    def get_embedding_model(self):
        pass

    @abstractmethod
    def get_llm(self):
        pass

    @abstractmethod
    def check_health(self):
        pass
    @abstractmethod
    def get_provider_name(self):
        pass
    # -------- EMBEDDINGS --------
    def generate_embeddings(self, texts: str | list[str]) -> list[float] | list[list[float]]:
        """
        Accepts a single string or a list of strings.
        Returns a single vector or a list of vectors respectively.
        """
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
        
        if isinstance(texts, str):
            return self.embedding_model.embed_query(texts)      # single vector
        return self.embedding_model.embed_documents(texts)      # batch vectors


    def get_context(self):
        return self.context
    def set_context(self,context:str):
        self.context = context

    # -------- LLM RESPONSE --------
    def generate_response(self, question: str) -> str:
        if not self.llm:
            raise ValueError("LLM not initialized")

        full_context = f"nRepository Context:\n{self.context}"

        prompt = f"""
        {full_context}

        Question:
        {question}

        Answer:
        """

        response = self.llm.invoke(prompt)
        return response.content

    # -------- QDRANT SETUP --------
    def init_vector_db(self, qdrant_client: QdrantHandler):
        """
        Initialize Qdrant client
        """
        if self.vector_db is None:
            self.vector_db = qdrant_client
    
    def store_repo_data(self, collection_name: str, repo_data: list[dict]) -> None:
        if not self.vector_db:
            raise ValueError("Qdrant client not initialized")
        if not repo_data:
            return

        BATCH_SIZE = 128  # increased for better throughput
        print(f"Storing {len(repo_data)} vectors in batches of size {BATCH_SIZE}")

        for batch_start in range(0, len(repo_data), BATCH_SIZE):
            batch = repo_data[batch_start: batch_start + BATCH_SIZE]
            texts = [item["text"] for item in batch]

            try:
                vectors = self.generate_embeddings(texts)
            except Exception as e:
                print(f"Batch {batch_start // BATCH_SIZE + 1} failed: {e}")
                continue

            ids = []
            payloads = []

            for item, vector in zip(batch, vectors):
                ids.append(item["id"])
                payloads.append({**item.get("metadata", {}),"text": item["text"][:1000]})

            try:
                print(f"Uploading batch starting at {batch_start}")
                self.vector_db.upload_collection(collection_name=collection_name,vectors=vectors,ids=ids,payload=payloads,batch_size=BATCH_SIZE,parallel=4)
            except Exception as e:
                print(f"Upload failed for batch starting at {batch_start}: {e}")
        
    def search_repo(self,collection_name: str,query: str,limit: int = 5):
        if not self.vector_db:
            raise ValueError("Qdrant client not initialized")

        query_vector = self.generate_embeddings(query)
        results = self.vector_db.search(collection_name=collection_name,query_vector=query_vector,limit=limit)
        return results