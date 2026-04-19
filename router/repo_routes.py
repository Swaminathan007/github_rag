from fastapi import APIRouter,Request
from .llm_init import get_llm
from models import Query,Response,RepoModel,RepoCollectionModel
from repoutils import RepoUtils
from utils import GithubUtils
repo_router = APIRouter(prefix="/repo")


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
        return Response(response="Invalid repository URL")
    if not GithubUtils.check_if_repo_exists(owner, reponame):
        return Response(response="Repository does not exist")
    
    #Clone repo and get content
    repo_content = GithubUtils.get_repo_content(repo.repo_url)
    if repo_content == []:
        return Response(response="Failed to get repository content")

    print(f"repo {reponame} cloned successfully and got embeddings")
    #Create collection
    collection_name = f"{owner}_{reponame}".lower().replace("-", "_").replace(".", "_") 
    llm_model.vector_db.create_collection(collection_name, 768)

    #Prepare repo data points from content
    repo_data = RepoUtils.prepare_repo_data(repo_content, repo.repo_url)

    #Store repo data points into collection
    llm_model.store_repo_data(collection_name, repo_data)

    return Response(response="Repository added successfully")
    
    

@repo_router.post("/{reponame}/query")
async def query_from_repo(reponame: str, query: Query):
    llm_model = get_llm()
    if(not llm_model.vector_db.collection_exists(reponame)):
        return Response(response="Repository does not exist,please add repo")
    
    #Get query string
    query_string = query.query

    #Search repo
    search_results = llm_model.search_repo(reponame, query_string, limit=5)
    context_parts = []
    for res in search_results:
        context_parts.append(res.payload.get("text", ""))
    context = "\n---\n".join(context_parts)

    #Set context
    llm_model.set_context(context)
    
    #Generate response
    llm_response = llm_model.generate_response(query_string)
    return Response(response=llm_response)
