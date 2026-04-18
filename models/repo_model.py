from pydantic import BaseModel

class RepoModel(BaseModel):
    repo_url: str