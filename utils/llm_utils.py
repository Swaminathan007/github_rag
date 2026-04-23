from redis_utils import RedisClient
from llm import OllamaHandler, GroqHandler
from loggingutils import Logger


class LLMUtils:
    _active_provider = None
    _active_provider_name = None
    __logger = Logger.get_logger(__name__)

    @classmethod
    def get_llm(cls):
        redis_client = RedisClient.get_redis_client()
        provider_name = redis_client.get("llm_provider")

        if not provider_name:
            raise ValueError("LLM provider not set in Redis")

        provider_name = provider_name.lower()

        # Return cached provider if unchanged
        if cls._active_provider and cls._active_provider_name == provider_name:
            cls.__logger.info("No change in LLM provider, returning existing provider")
            return cls._active_provider

        # Initialize provider based on value
        if provider_name == OllamaHandler.get_provider_name():
            cls.__logger.info("Initializing Ollama provider")
            cls._active_provider = OllamaHandler()

        elif provider_name == GroqHandler.get_provider_name():
            cls.__logger.info("Initializing Groq provider")
            cls._active_provider = GroqHandler()

        else:
            raise ValueError(f"LLM provider '{provider_name}' not supported")

        cls._active_provider_name = provider_name
        return cls._active_provider

    @classmethod
    def generate_response_for_query(
        cls, query_string: str, llm_model, reponame: str
    ) -> str:
        redis_client = RedisClient.get_redis_client()
        if not llm_model.vector_db.collection_exists(reponame):
            return "Repository does not exist, please add repo"

        # Generate embeddings
        query_embedding = llm_model.generate_embeddings(query_string)

        # Check semantic cache
        cached_response = redis_client.get_semantic(
            repo=reponame, query_embedding=query_embedding
        )

        if cached_response:
            return cached_response

        search_results = llm_model.search_repo(reponame, query_string, limit=5)

        context_parts = [res.payload.get("text", "") for res in search_results]
        context = "\n---\n".join(context_parts)

        llm_model.set_context(context)

        llm_response = llm_model.generate_response(query_string)

        redis_client.set_semantic(
            repo=reponame,
            query=query_string,
            embedding=query_embedding,
            response=llm_response,
        )
        return llm_response
