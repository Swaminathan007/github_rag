from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from typing import List, Dict, Any
from utils import HttpConnection
from qdrant_client.models import PointStruct
import uuid
from loggingutils import Logger

class QdrantHandler:
    _embedding_key = "vector"
    __logger = Logger.get_logger(__name__)
    def __init__(self,url:str,api_key:str):
        self.url = url
        self.api_key = api_key
        self.client = QdrantClient(url=self.url,api_key=self.api_key)
        
    def create_collection(self, collection_name: str, vector_size: int = 768):
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(collection_name=collection_name,vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE))
    
    def upsert(self, collection_name: str, points: List[Dict[str, Any]]):
        uuid_points = [PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_DNS, str(point["id"]))),vector=point[QdrantHandler.get_embedding_key()],payload=point["payload"]) for point in points]
        self.client.upsert(collection_name=collection_name,points=uuid_points)
        
    def search(self, collection_name: str, query_vector: List[float], limit: int = 5):
        results = self.client.query_points(collection_name=collection_name,query=query_vector,limit=limit)
        return results.points 

    def check_health(self):
        try:
            url = self.url
            http_client = HttpConnection(url+"/healthz")
            http_client.get()
            return http_client.response_code == 200
        except Exception as e:
            self.__logger.error(e)
            return False
    def get_all_collections(self,limit:int=10,offset:int=0) -> List[str]:
        try:
            response = self.client.get_collections()
            collections = response.collections[offset:offset+limit]
            return [collection.name for collection in collections]
        except Exception as e:
            self.__logger.error(e)
            return []
    
    def collection_exists(self,collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)
    
    def upload_collection(self,collection_name: str,vectors,ids,payload,batch_size: int = 128,parallel: int = 4):
        try:
            points = [PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_DNS, str(id_))),vector=vector,payload=pl) for id_, vector, pl in zip(ids, vectors, payload)]
            self.client.upload_points(collection_name=collection_name,points=points,batch_size=batch_size,parallel=parallel)
        except Exception as e:
            raise RuntimeError("Error uploading collection") from e
    
    def delete_collection(self,collection_name: str):
        try:
            self.client.delete_collection(collection_name=collection_name)
        except Exception as e:
            self.__logger.error(e)
            raise RuntimeError("Error deleting collection") from e
    @classmethod
    def get_embedding_key(cls):
        return cls._embedding_key