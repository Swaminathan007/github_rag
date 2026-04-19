from pydantic import BaseModel
class RedisModel(BaseModel):
    key: str
    val: str
class RedisDeleteModel(BaseModel):
    key: str