import redis
from config import Config


class RedisClient:
    _instance = None

    def __init__(self):
        self.client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=False  # we manually decode
        )

    def set(self, key: str, value: str):
        try:
            self.client.set(key, value)
        except Exception as e:
            print(e)

    def get(self, key: str) -> str:
        try:
            value = self.client.get(key)
            return value.decode("utf-8") if value else ""
        except Exception as e:
            print(e)
            return ""

    def delete(self, key: str):
        try:
            self.client.delete(key)
        except Exception as e:
            print(e)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def get_all(self) -> list:
        try:
            keys = self.client.keys()
            return [k.decode("utf-8") for k in keys]
        except Exception as e:
            print(e)
            return []

    @classmethod
    def get_redis_client(cls):
        if cls._instance is None:
            cls._instance = RedisClient()
        return cls._instance

