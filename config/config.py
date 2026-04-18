import os
from dotenv import load_dotenv
import subprocess
load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL")


    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    REPO_BASE = os.getenv("REPO_BASE") or "/tmp/repos"
    subprocess.run(["mkdir", "-p", REPO_BASE])

    if LLM_PROVIDER is None or QDRANT_URL is None:
        raise ValueError("LLM provider or Qdrant url is not set")
    
    if LLM_PROVIDER == "ollama":
        if OLLAMA_BASE_URL is None or OLLAMA_MODEL is None or OLLAMA_EMBEDDING_MODEL is None:
            raise ValueError("Ollama environment variables are not set")
    
    if LLM_PROVIDER == "groq":
        if GROQ_API_KEY is None or GROQ_MODEL is None or OLLAMA_EMBEDDING_MODEL is None:
            raise ValueError("Groq environment variables are not set")

