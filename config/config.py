import os
from dotenv import load_dotenv
import subprocess
load_dotenv()

class Config:
    
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    REPO_BASE = os.getenv("REPO_BASE") or "/tmp/repos"

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")


    subprocess.run(["mkdir", "-p", REPO_BASE])

    if QDRANT_URL is None:
        raise ValueError("Qdrant environment variables are not set")
        
    if REDIS_HOST is None or REDIS_PORT is None:
        raise ValueError("Redis environment variables are not set")

