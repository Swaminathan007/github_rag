from pydantic import BaseModel

class Response(BaseModel):
    response: str
    repo_name: str

class QueryResponse(BaseModel):
    response: str