from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from .llm_init import get_llm
from models import Query, Response, RepoModel, RepoCollectionModel, QueryResponse
from repoutils import RepoUtils
from utils import GithubUtils, LLMUtils
from loggingutils import Logger

from repoutils import GithubRepo,RepoStatusEnum
repo_router = APIRouter(prefix="/repo")
logger = Logger.get_logger(__name__)


@repo_router.get("/get_all_repos")
async def get_all_repos(request: Request):
    limit = int(request.query_params.get("limit", 10))
    offset = int(request.query_params.get("offset", 0))
    return RepoCollectionModel(
        collection_list=await run_in_threadpool(
            get_llm().vector_db.get_all_collections, limit=limit, offset=offset
        )
    )


@repo_router.get("/{reponame}")
async def get_repo(reponame: str):
    llm_model = get_llm()
    exists = await run_in_threadpool(llm_model.vector_db.collection_exists, reponame)
    return {"reponame": "exists" if exists else "does not exist"}


@repo_router.post("/add")
async def add_repo(repo: RepoModel):
    llm_model = get_llm()    
    # Heavy I/O — offload to thread
    repository = None
    if(repo.repo_url.startswith("https://github.com/")):
        repository = GithubRepo(repo.repo_url,repo.branch)
    else:
        return Response(response="Failed to get repository",repo_name="",code=400)
    
    if(not repository.check_if_repo_exists()):
        return Response(response="Repo does not exists",repo_name="",code=400)
    
    collection_name = repository._get_repo_collection_path(repo.branch)
    cmd_status = repository.clone_repo()
    if cmd_status == RepoStatusEnum.FAILED:
            return Response(response=cmd_status.get_formatted_status(),repo_name="",code=400)
    if cmd_status == RepoStatusEnum.EXISTS and llm_model.vector_db.collection_exists(collection_name):
        return Response(response=cmd_status.get_formatted_status(),repo_name="",code=400)
    
    try:
        await run_in_threadpool(llm_model.vector_db.create_collection, collection_name, 768)

        repository.generate_repo_files()
        repository.generate_file_vectors()

        await run_in_threadpool(llm_model.store_repo_data, collection_name, repository.vectors)
        return Response(response="Repository added successfully", repo_name=repo.repo_url, code=201)
    
    except Exception as e:        
        return Response(response=f"Error while updating or creating repo collection: {e}",repo_name=repo.repo_url,code=500)

@repo_router.post("/{reponame}/query")
async def query_from_repo(reponame: str, query: Query):
    try:
        # ✅ Ollama inference runs in a thread — won't block other requests
        response = await run_in_threadpool(LLMUtils.generate_response_for_query, query.query, get_llm(), reponame)
        return QueryResponse(response=response, code=200)
    except Exception as e:
        return QueryResponse(response=str(e), code=400)


@repo_router.delete("/delete/{repo}")
async def delete_repo(repo: str):
    llm_model = get_llm()
    exists = await run_in_threadpool(llm_model.vector_db.collection_exists, repo)
    if not exists:
        return Response(response=f"{repo} does not exist", repo_name=repo, code=400)
    await run_in_threadpool(llm_model.vector_db.delete_collection, repo)
    return Response(response=f"{repo} deleted successfully", repo_name=repo, code=200)