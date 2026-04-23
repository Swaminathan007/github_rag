import redis
import json
import numpy as np
from typing import List, Optional
from config import get_config
from qdrantutils import QdrantHandler
from loggingutils import Logger

def cosine_similarity(a: List[float], b: List[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


class RedisClient:
    __logger=Logger.get_logger(__name__)
    _instance = None

    # soft limits (app-level)
    _cache_limit = 400
    _ttl_seconds = 60 * 60 * 24  # 24 hours

    def __init__(self):
        self.client = redis.Redis(
            host=get_config().redis_host,
            port=get_config().redis_port,
            decode_responses=False
        )

    # -------------------------
    # Basic KV methods
    # -------------------------
    def set(self, key: str, value: str, ttl: Optional[int] = None):
        try:
            self.client.set(
                key,
                value,
                ex=ttl or self._ttl_seconds
            )
        except Exception as e:
            self.__logger.error(e)

    def get(self, key: str) -> str:
        try:
            value = self.client.get(key)
            return value.decode("utf-8") if value else ""
        except Exception as e:
            self.__logger.error(e)
            return ""

    def delete(self, key: str):
        try:
            self.client.delete(key)
        except Exception as e:
            self.__logger.error(e)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def get_all(self) -> list:
        try:
            keys = self.client.keys()
            return [k.decode("utf-8") for k in keys]
        except Exception as e:
            self.__logger.error(e)
            return []


    def _repo_key(self, repo: str) -> str:
        return f"semantic_cache:{repo}"

    def _get_repo_cache(self, repo: str) -> list:
        try:
            raw = self.client.get(self._repo_key(repo))
            if not raw:
                return []
            return json.loads(raw.decode("utf-8"))
        except Exception as e:
            self.__logger.error(e)
            return []

    def _set_repo_cache(self, repo: str, data: list):
        try:
            self.client.set(
                self._repo_key(repo),
                json.dumps(data),
                ex=self._ttl_seconds  # TTL refresh on write
            )
        except Exception as e:
            self.__logger.error(e)

    def get_semantic(self,repo: str,query_embedding: List[float],threshold: float = 0.85) -> Optional[str]:

        try:
            cache = self._get_repo_cache(repo)

            best_score = 0.0
            best_match = None

            for item in cache:
                score = cosine_similarity(query_embedding,item[QdrantHandler.get_embedding_key()])

                if score > best_score:
                    best_score = score
                    best_match = item

            if best_score >= threshold and best_match:
                # touch key to keep it hot (pseudo-LRU)
                self.client.expire(self._repo_key(repo), self._ttl_seconds)
                return best_match["response"]

            return None

        except Exception as e:
            self.__logger.error(e)
            return None


    def set_semantic(self,repo: str,query: str,embedding: List[float],response: str):
        try:
            cache = self._get_repo_cache(repo)

            cache.append({"query": query,QdrantHandler.get_embedding_key(): embedding,"response": response})
            if len(cache) > self._cache_limit:
                cache = cache[-self._cache_limit:]

            self._set_repo_cache(repo, cache)

        except Exception as e:
            self.__logger.error(e)

    def clear_repo_cache(self, repo: str):
        try:
            self.client.delete(self._repo_key(repo))
        except Exception as e:
            self.__logger.error(e)

    @classmethod
    def get_redis_client(cls):
        if cls._instance is None:
            cls._instance = RedisClient()
        return cls._instance