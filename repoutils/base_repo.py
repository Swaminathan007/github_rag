#Repo base class
from abc import ABC,abstractmethod
from enum import Enum
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from config import get_config
import subprocess
import os
from loggingutils import Logger

class RepoStatusEnum(Enum):
    CLONED = (1,"cloned","Repo cloned successfully")
    UPDATED = (2,"updated","Repo updated to latest commit")
    FAILED = (3,"failed","Failed to clone repo")
    EXISTS = (4,"exists","Repo already upto date in branch")


    def __init__(self, status: int, status_name: str, formatted_status: str):
        self.status = status
        self.status_name = status_name
        self.formatted_status = formatted_status


    def get_formatted_status(self):
        return self.formatted_status
    
    def get_status(self):
        return self.status
    
    def get_status_name(self):
        return self.get_status_name
    
    @classmethod
    def get_from_id(cls, status: int) -> "RepoStatusEnum":
        for item in cls:
            if item.get_status() == status:
                return item 
        raise ValueError("Id not found in enum")


class BaseRepo(ABC):
    __logger = Logger.get_logger(__name__)
    def __init__(self,repo_url: str,branch: str):
        self.repo_url = repo_url 
        self.owner = None 
        self.repo_name = None 
        self.files = []
        self.vectors = []
        self.branch = branch
        self.repo_cloned_path = ""
    
    ## Abstract methods
    @abstractmethod
    def get_owner_and_repo(self) -> (str,str):
        pass
    @abstractmethod
    def check_if_repo_exists(self) -> bool:
        pass
    @abstractmethod
    def _get_repo_collection_path(self, branch:str) -> str:
        pass

    ## Non abstract methods
    def get_repo_url(self) -> str:
        return self.repo_url
    def set_repo_url(self,url:str):
        self.repo_url = url.rstrip(".git").rstrip("/")
    def get_repo_cloned_path(self) -> str:
        return self.repo_cloned_path
    def set_repo_cloned_path(self,repo_cloned_path:str):
        self.repo_cloned_path = repo_cloned_path
    def clone_repo(self) -> RepoStatusEnum:
        try:
            if not self.check_if_repo_exists():
                return RepoStatusEnum.FAILED

            repo_clone_path = self._get_repo_collection_path("")
            repo_path = f"{get_config().repo_base}/{repo_clone_path}"
            self.set_repo_cloned_path(repo_path)
            # 🔁 If repo already exists → update
            if os.path.exists(repo_path):
                self.__logger.info("Repo exists, checking for updates...")

                subprocess.run(["git", "fetch"], cwd=repo_path, check=True)

                checkout = subprocess.run(["git", "checkout", self.branch],cwd=repo_path, capture_output=True,text=True)

                if checkout.returncode != 0:
                    self.__logger.info(f"Creating tracking branch: {self.branch}")
                    subprocess.run(
                        ["git", "checkout", "-b", self.branch, f"origin/{self.branch}"],
                        cwd=repo_path,
                        check=True
                    )

                pull = subprocess.run(
                    ["git", "pull"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )

                if "Already up to date." in pull.stdout:
                    self.__logger.info("Repo already up-to-date.")
                    return RepoStatusEnum.EXISTS
                else:
                    self.__logger.info("Repo updated to latest commit.")
                    return RepoStatusEnum.UPDATED

            # 📥 First-time clone
            self.__logger.info("Cloning repo for the first time...")

            clone_cmd = ["git", "clone"]

            if self.branch and self.branch.strip():
                clone_cmd.extend(["--branch", self.branch])

            clone_cmd.extend([self.repo_url, repo_clone_path])

            self.__logger.debug(f"Clone command: {clone_cmd}")

            subprocess.run(clone_cmd,cwd=get_config().repo_base,check=True)
            return RepoStatusEnum.CLONED

        except subprocess.CalledProcessError as e:
            self.__logger.error(f"Git command failed: {e}")
            return RepoStatusEnum.FAILED

        except Exception as e:
            self.__logger.error(f"Unexpected error: {e}")
            return RepoStatusEnum.FAILED
    
    def generate_repo_files(self):
        try:
            if(not os.path.exists(self.get_repo_cloned_path())):
                raise ValueError("Repo not cloned")
            self.files = []
            for root, dirs, files in os.walk(self.get_repo_cloned_path()):
                if ".git" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_data = {
                                "path": file_path,
                                "content": f.read()
                            }
                            self.files.append(file_data)
                    except Exception as e:
                        self.__logger.error(f"Error reading file {file_path}: {e}")
                        continue
        except Exception as e:
            self.__logger.error(f"Error getting repo content: {e}")
            self.files = []

    def generate_file_vectors(self):
        if(len(self.files) == 0):
            raise ValueError("No files found")
        
        try:
            self.vectors = []

            for i, item in enumerate(self.files):
                chunks = BaseRepo.chunk_text(item["content"])

                for j, chunk in enumerate(chunks):
                    self.vectors.append({
                        "id": f"{i}_{j}",  
                        "text": f"File: {item['path']}\n\n{chunk}",
                        "metadata": {
                            "path": item["path"],
                            "repo": self.repo_url,
                            "chunk_index": j,
                            "branch": self.branch
                        }
                    })
        except Exception as e:
            self.__logger.error(f"Error generating vectors: {e}")
            self.files = []

    ##Class methods
    @classmethod
    def chunk_text(cls,text: str):
        splitter = RecursiveCharacterTextSplitter(chunk_size=800,chunk_overlap=200)
        return splitter.split_text(text)
        
    

