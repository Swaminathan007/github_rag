from pydantic import BaseModel

class Response(BaseModel):
    response: str
    repo_name: str
    code: int

class QueryResponse(BaseModel):
    response: str
    code: int