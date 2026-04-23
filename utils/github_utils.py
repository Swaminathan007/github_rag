from .httpconnection import HttpConnection
import json
from config import get_config
import os
import subprocess
import shutil
from loggingutils import Logger


class GithubUtils:
    __logger = Logger.get_logger(__name__)

    @classmethod
    def check_if_repo_exists(cls, owner: str, reponame: str) -> bool:
        try:
            http_client = HttpConnection(
                f"https://api.github.com/repos/{owner}/{reponame}"
            )
            http_client.get()
            return http_client.response_code == 200
        except Exception as e:
            cls.__logger.error(e)
            return False

    @classmethod
    def get_owner_and_repo(cls, repo: str) -> tuple[str, str]:
        try:
            repo = repo.replace("https://github.com/", "")
            cls.__logger.info(f"Repo: {repo}")
            owner, reponame = repo.split("/")
            return owner, reponame
        except Exception as e:
            cls.__logger.error(e)
            return "", ""

    @classmethod
    def get_repo_content(cls, repo: str) -> list:
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo)
            if (
                owner == ""
                or reponame == ""
                or not GithubUtils.check_if_repo_exists(owner, reponame)
            ):
                return []

            # Recursive content fetching
            all_files = []
            repo_path = GithubUtils._clone_repo(repo)
            if repo_path == "":
                return []
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            all_files.append({"path": file_path, "content": f.read()})
                    except Exception as e:
                        cls.__logger.error(f"Error reading file {file_path}: {e}")
                        continue
            return all_files
        except Exception as e:
            cls.__logger.error(f"Error getting repo content: {e}")
            return []

    @classmethod
    def get_default_branch(cls, repo: str) -> str:
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo)
            if (
                owner == ""
                or reponame == ""
                or not GithubUtils.check_if_repo_exists(owner, reponame)
            ):
                return ""
            http_client = HttpConnection(
                f"https://api.github.com/repos/{owner}/{reponame}"
            )
            http_client.get()
            response_dict = json.loads(http_client.response_content)
            return str(response_dict["default_branch"])
        except Exception as e:
            cls.__logger.error(e)
            return ""

    # Repo cloning
    @classmethod
    def _clone_repo(cls, repo_url: str) -> str:
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo_url)
            if (
                owner == ""
                or reponame == ""
                or not GithubUtils.check_if_repo_exists(owner, reponame)
            ):
                return ""
            repo_path = f"{get_config().repo_base}/{reponame}"
            if os.path.exists(repo_path):
                cls.__logger.info("Repo already exists, pulling latest changes....")
                subprocess.run(["git", "pull"], cwd=repo_path, check=True)
                return repo_path
            cls.__logger.info("Cloning repo for the first time....")
            subprocess.run(["git", "clone", repo_url], cwd=get_config().repo_base, check=True)
            return repo_path
        except Exception as e:
            cls.__logger.error(e)
            return ""

    @classmethod
    def _delete_repo(cls, repo_url: str) -> bool:
        try:
            owner, reponame = GithubUtils.get_owner_and_repo(repo_url)
            if (
                owner == ""
                or reponame == ""
                or not GithubUtils.check_if_repo_exists(owner, reponame)
            ):
                return False
            repo_path = f"{get_config().repo_base}/{reponame}"
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                return True
            return False
        except Exception as e:
            cls.__logger.error(e)
            return False
