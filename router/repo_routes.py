from fastapi import APIRouter,Request
from .llm_init import get_llm
from models import Query,Response,RepoModel,RepoCollectionModel,QueryResponse
from repoutils import RepoUtils
from utils import GithubUtils,LLMUtils
from loggingutils import Logger
repo_router = APIRouter(prefix="/repo")

logger = Logger.get_logger(__name__)
@repo_router.get("/get_all_repos")
async def get_all_repos(request: Request):
    limit = int(request.query_params.get("limit", 10))
    offset = int(request.query_params.get("offset", 0))
    return RepoCollectionModel(collection_list=get_llm().vector_db.get_all_collections(limit=limit,offset=offset))

@repo_router.get("/{reponame}")
async def get_repo(reponame: str):
    llm_model = get_llm()
    if(llm_model.vector_db.collection_exists(reponame)):
        return {"reponame": "exists"}
    return {"reponame": "does not exist"}

@repo_router.post("/add")
async def add_repo(repo: RepoModel):
    llm_model = get_llm()
    #Check for valid repo
    owner,reponame = GithubUtils.get_owner_and_repo(repo.repo_url)
    if owner == "" or reponame == "":
        return Response(response="Invalid repository URL",repo_name="",code=400)
    if not GithubUtils.check_if_repo_exists(owner, reponame):
        return Response(response="Repository does not exist",repo_name="",code=400)
    
    #Clone repo and get content
    repo_content = GithubUtils.get_repo_content(repo.repo_url)
    if repo_content == []:
        return Response(response="Failed to get repository content",repo_name="",code=400)

    logger.info(f"repo {reponame} cloned successfully and got embeddings")
    #Create collection
    collection_name = f"{owner}_{reponame}".lower().replace("-", "_").replace(".", "_") 
    llm_model.vector_db.create_collection(collection_name, 768)

    #Prepare repo data points from content
    repo_data = RepoUtils.prepare_repo_data(repo_content, repo.repo_url)

    #Store repo data points into collection
    llm_model.store_repo_data(collection_name, repo_data)

    return Response(response="Repository added successfully",repo_name=collection_name,code=201)
    
    

@repo_router.post("/{reponame}/query")
async def query_from_repo(reponame: str, query: Query):
    try:
        return QueryResponse(response=LLMUtils.generate_response_for_query(query.query,get_llm(),reponame),code=200)
    except Exception as e:
        return QueryResponse(response=str(e),code=400)

@repo_router.delete("/delete/{repo}")
async def delete_repo(repo: str):
    llm_model = get_llm()
    if(not llm_model.vector_db.collection_exists(repo)):
        return Response(response=f"{repo} does not exist",repo_name=repo,code=400)
    llm_model.vector_db.delete_collection(repo)
    return Response(response=f"{repo} deleted successfully",repo_name=repo,code=200)
