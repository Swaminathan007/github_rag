import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path


@dataclass
class Config:
    # Qdrant
    qdrant_url: str
    qdrant_api_key: str | None

    # Repo
    repo_base: Path

    # Redis
    redis_host: str
    redis_port: int

    # RustFS
    rustfs_access_key: str
    rustfs_secret: str
    rustfs_bucket: str
    rustfs_port: int

    @classmethod
    def load(cls) -> "Config":
        load_dotenv()

        repo_base = Path(os.getenv("REPO_BASE", "/tmp/repos"))

        config = cls(
            qdrant_url=cls._require("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            repo_base=repo_base,
            redis_host=cls._require("REDIS_HOST"),
            redis_port=int(cls._require("REDIS_PORT")),
            rustfs_access_key=cls._require("RUSTFS_ACCESS_KEY"),
            rustfs_secret=cls._require("RUSTFS_SECRET"),
            rustfs_bucket=cls._require("RUSTFS_BUCKET"),
            rustfs_port=int(cls._require("RUSTFS_PORT")),
        )

        config._post_init()
        return config

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    def _post_init(self):
        self.repo_base.mkdir(parents=True, exist_ok=True)

        if not self.qdrant_url.startswith("http"):
            raise ValueError("QDRANT_URL must be a valid URL")

        if self.redis_port <= 0:
            raise ValueError("REDIS_PORT must be a positive integer")

        if self.rustfs_port <= 0:
            raise ValueError("RUSTFS_PORT must be a positive integer")

config = None
def get_config() -> Config:
    global config
    if config is None:
        config = Config.load()
    return config