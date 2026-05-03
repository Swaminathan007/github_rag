
from .base_repo import BaseRepo
from loggingutils import Logger
from utils import HttpConnection

class GithubRepo(BaseRepo):
    __logger = Logger.get_logger(__name__)
    def __init__(self,repo_url: str,branch: str):
        super().__init__(repo_url,branch)
        self.prefix = "https://github.com/"
        self.type = "github"
    
    def get_owner_and_repo(self) -> (str,str):
        try:
            repo = self.repo_url.replace(self.prefix, "")
            self.owner, self.repo_name = repo.split("/")
            return self.owner, self.repo_name
        except Exception as e:
            self.__logger.error(e)
            return "", ""
    
    def check_if_repo_exists(self) -> bool:
        try:
            self.get_owner_and_repo()
            if(self.owner == "" or self.repo_name == ""):
                return False
            http_client = HttpConnection(f"https://api.github.com/repos/{self.owner}/{self.repo_name}")
            http_client.get()
            return http_client.response_code == 200
        except Exception as e:
            self.__logger.error(e)
            return False
    def _get_repo_collection_path(self,branch:str) -> str:
        return f"{self.type}_{self.owner}_{self.repo_name}_{branch}".replace("-","_").replace(".","_")