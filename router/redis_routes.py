from redis_utils import RedisClient
from fastapi import APIRouter
from models import RedisModel,RedisDeleteModel,Response

redis_router = APIRouter(prefix="/redis")



@redis_router.post("/set")
def set_redis(redis_model: RedisModel):
    RedisClient.get_redis_client().set(redis_model.key, redis_model.val)
    return Response(message="Key set successfully")

@redis_router.post("/delete")
def delete_redis(redis_model: RedisDeleteModel):
    RedisClient.get_redis_client().delete(redis_model.key)
    return Response(message="Key deleted successfully")

@redis_router.get("/get")
def get_redis(key: str):
    return {"val":RedisClient.get_redis_client().get(key)}


@redis_router.get("/settings")
def get_all_redis():
    redis_client = RedisClient.get_redis_client()
    llm_provider = redis_client.get("llm_provider")
    if(llm_provider is None):
        return {"llm_provider":None}
    elif llm_provider == "ollama":
        return {"llm_provider":"ollama","ollama_model":redis_client.get("ollama_model")}
    elif llm_provider == "groq":
        return {"llm_provider":"groq","groq_model":redis_client.get("groq_model")}
    return {"llm_provider":llm_provider}
