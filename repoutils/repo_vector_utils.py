from langchain_classic.text_splitter import RecursiveCharacterTextSplitter

class RepoUtils:
    def chunk_text(text: str):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,     
            chunk_overlap=200
        )
        return splitter.split_text(text)
    def get_repo_vectors(repo_content, repo_url) -> list:
        repo_data = []

        for i, item in enumerate(repo_content):
            chunks = RepoUtils.chunk_text(item["content"])

            for j, chunk in enumerate(chunks):
                repo_data.append({
                    "id": f"{i}_{j}",  
                    "text": f"File: {item['path']}\n\n{chunk}",
                    "metadata": {
                        "path": item["path"],
                        "repo": repo_url,
                        "chunk_index": j
                    }
                })

        return repo_data