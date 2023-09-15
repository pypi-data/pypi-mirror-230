import os

from git import InvalidGitRepositoryError, Repo

from solidipes.utils import get_git_repository, get_git_root


class GitInfos:
    def __init__(self):
        self.git_origin = None
        self.git_root = None
        self.git_repository = None
        try:
            self.git_root = get_git_root()
            self.git_repository = get_git_repository()
            self._set_gitlab_uri()
        except InvalidGitRepositoryError:
            pass

    def _set_gitlab_uri(self):
        dir_path = os.getcwd()
        self.git_repository = Repo(dir_path, search_parent_directories=True)
        remotes = self.git_repository.remotes
        if "origin" not in remotes:
            return
        git_origin = [e for e in remotes.origin.urls][0]
        if git_origin.startswith("git@"):
            git_origin = git_origin.replace("git@", "")
            _split = git_origin.split(":")
            git_origin = "https://" + _split[0] + "/gitlab/" + _split[1]
        self.git_origin = git_origin.replace(".git", "")


################################################################
