from config import Config
from utils.github_utils import GithubUtils
from repoutils import RepoUtils
from llm import LLMUtils
def main():
    print("=============================================== GitHub RAG System ===============================================")
    
    provider = Config.LLM_PROVIDER
    handler = LLMUtils.get_llm()

    # Check health
    if not handler.check_health():
        print(f"Error: {provider} handler is not healthy or reachable.")
        return
    print(f"LLM provider: {provider} is healthy,checking vector db health")
    if not handler.vector_db.check_health():
        print("Error: Qdrant handler is not healthy or reachable.")
        return

    print("Vector db is healthy")

    #Get GitHub Repo URL
    repo_url = input("Enter GitHub Repository URL: ").strip()
    if not repo_url:
        print("Invalid URL.")
        return

    owner, reponame = GithubUtils.get_owner_and_repo(repo_url)
    if not owner or not reponame:
        print("Could not parse repository URL.")
        return

    print(f"Fetching content from {owner}/{reponame}...")
    repo_content = GithubUtils.get_repo_content(repo_url)
    if not repo_content:
        print("No content found or repository is private/inaccessible.")
        return

    collection_name = f"{owner}_{reponame}".lower().replace("-", "_").replace(".", "_")
    
    print(f"Storing {len(repo_content)} files into Qdrant collection '{collection_name}'...")
    
    # Determine vector size
    vector_size = 768
    
    # Create collection
    handler.vector_db.create_collection(collection_name, vector_size)
    
    # Prepare data for upsert
    repo_data = RepoUtils.prepare_repo_data(repo_content, repo_url)
    handler.store_repo_data(collection_name, repo_data)
    print("Ingestion complete.")
    collection_name = "burntsushi_ripgrep"
    # Query Loop
    print("\nYou can now ask questions about the repository. Type 'q' or 'quit' to exit.")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in ['q', 'quit']:
            print("Exiting...")
            break
        
        if not question:
            continue

        print("Searching for relevant context...")
        search_results = handler.search_repo(collection_name, question, limit=5)
        
        context_parts = []
        for res in search_results:
            context_parts.append(res.payload.get("text", "")) 
        
        context = "\n---\n".join(context_parts)
        handler.set_context(context)
        
        print("Generating response...")
        response = handler.generate_response(question)
        print(f"\nAnswer: {response}")

if __name__ == "__main__":
    main()
    
