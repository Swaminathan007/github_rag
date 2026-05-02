from .httpconnection import HttpConnection
from config import get_config
import os
import subprocess
import shutil
from loggingutils import Logger
class GithubUtils:
    CLONE_SUCCESS = 0
    UPDATED = 1
    NO_CHANGE = 2
    FAILED = -1

    __logger = Logger.get_logger(__name__)

    @classmethod
    def check_if_repo_exists(cls, owner: str, reponame: str) -> bool:
        try:
            http_client = HttpConnection(f"https://api.github.com/repos/{owner}/{reponame}")
            http_client.get()
            return http_client.response_code == 200
        except Exception as e:
            cls.__logger.error(e)
            return False

    @classmethod
    def get_owner_and_repo(cls, repo: str) -> tuple[str, str]:
        try:
            repo = repo.replace("https://github.com/", "")
            owner, reponame = repo.split("/")
            return owner, reponame
        except Exception as e:
            cls.__logger.error(e)
            return "", ""

    @classmethod
    def get_repo_content(cls, repo: str, branch: str = None) -> (list, int):
        try:
            owner,repo_name = GithubUtils.get_owner_and_repo(repo)
            if not GithubUtils.check_if_repo_exists(owner,repo_name):
                return [], cls.FAILED

            exit_code, repo_path = GithubUtils._clone_repo(repo, branch)

            # No changes → skip processing
            if exit_code not in (GithubUtils.CLONE_SUCCESS, GithubUtils.UPDATED):
                cls.__logger.info("No changes in repo, skipping content extraction")
                return [], cls.NO_CHANGE

            if not repo_path:
                return [], cls.FAILED

            cls.__logger.info("Changes detected, extracting repository content...")

            all_files = []

            for root, dirs, files in os.walk(repo_path):

                if ".git" in root:
                    continue

                for file in files:
                    file_path = os.path.join(root, file)


                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            all_files.append({
                                "path": file_path,
                                "content": f.read()
                            })
                    except Exception as e:
                        cls.__logger.error(f"Error reading file {file_path}: {e}")
                        continue

            # ✅ Return success WITH exit code
            return all_files, exit_code

        except Exception as e:
            cls.__logger.error(f"Error getting repo content: {e}")
            return [], cls.FAILED
    @classmethod
    def check_is_valid_repo_url(cls, repo_url: str) -> bool:
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo_url)
            if (owner == "" or reponame == "" or not GithubUtils.check_if_repo_exists(owner, reponame)):
                return False
            return True
        except Exception as e:
            cls.__logger.error(e)
            return False
    # Repo cloning
    @classmethod
    def _clone_repo(cls, repo_url: str, branch: str = None):
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo_url)

            if not GithubUtils.check_is_valid_repo_url(repo_url):
                return cls.FAILED, ""
            
            repo_clone_path = GithubUtils.get_repo_collection_name(reponame,owner,"")

            repo_path = f"{get_config().repo_base}/{repo_clone_path}"

            # Case 1: Repo already exists
            if os.path.exists(repo_path):
                cls.__logger.info("Repo exists, checking for updates...")

                # Fetch latest changes
                subprocess.run(["git", "fetch"], cwd=repo_path, check=True)

                # Check if there are changes
                status = subprocess.run(["git", "status", "-uno"],cwd=repo_path,capture_output=True,text=True)
                if "behind" in status.stdout:
                    cls.__logger.info("Changes detected, pulling latest...")
                    subprocess.run(["git", "pull"], cwd=repo_path, check=True)
                    return cls.UPDATED, repo_path
                else:
                    cls.__logger.info("Repo already up-to-date.")
                    return cls.NO_CHANGE, repo_path

            # Case 2: Fresh clone
            cls.__logger.info("Cloning repo for the first time...")

            clone_cmd = ["git", "clone",repo_url]
    
            if branch and branch.strip():
                clone_cmd.extend(["--branch", branch])
            clone_cmd.append(repo_clone_path)
            cls.__logger.debug(f"Clone command: {clone_cmd}")
            subprocess.run(clone_cmd, cwd=get_config().repo_base, check=True)

            return cls.CLONE_SUCCESS, repo_path

        except subprocess.CalledProcessError as e:
            cls.__logger.error(f"Git command failed: {e}")
            return cls.FAILED, ""
        except Exception as e:
            cls.__logger.error(f"Unexpected error: {e}")
            return cls.FAILED, ""

    @classmethod
    def _delete_repo(cls, repo_url: str) -> bool:
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo_url)
            if (not GithubUtils.check_is_valid_repo_url(repo_url)):
                return False
            repo_path = f"{get_config().repo_base}/{GithubUtils.get_repo_collection_name(reponame,owner,"")}"
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                return True
            return False
        except Exception as e:
            cls.__logger.error(e)
            return False
    @classmethod
    def get_repo_collection_name(cls,repo_name: str,owner: str,branch:str) -> str:
        return f"{owner}_{repo_name}_{branch}".lower().replace("-", "_").replace(".", "_")
    
