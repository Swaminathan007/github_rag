from pydantic import BaseModel

class RepoModel(BaseModel):
    repo_url: str


class RepoCollectionModel(BaseModel):
    collection_list: list
    