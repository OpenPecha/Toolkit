import enum
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List

from git import Repo
from github import Github


class Storages(enum.Enum):
    GITHUB = enum.auto()


def _getenv(name, optional):
    env = os.getenv(name)
    if env:
        return env
    elif optional:
        return env
    else:
        raise RuntimeError(f"Please set {name} environment variable")


def _get_value(value, env_name, optional=False):
    return value if value else _getenv(env_name, optional)


def get_authenticated_remote_url(url, org, token):
    old_url = url.split("//")
    auth_remote_url = f"{old_url[0]}//{org}:{token}@{old_url[1]}"
    return auth_remote_url


def setup_auth_for_new_repo(repo, org, token, remote_url):
    auth_remote_url = get_authenticated_remote_url(remote_url, org, token)
    repo.create_remote("origin", auth_remote_url)
    return repo


def is_repo_authenticated(repo) -> bool:
    remote_url = repo.remote().url
    if "@" in remote_url:
        return True
    return False


def setup_auth_for_old_repo(repo, org, token):
    remote_url = repo.remote().url
    if is_repo_authenticated(repo):
        return repo
    auth_remote_url = get_authenticated_remote_url(remote_url, org, token)
    repo.remote().set_url(auth_remote_url)
    return repo


def commit_and_push(repo, message, branch="master"):
    repo.git.add("-A")
    repo.git.commit("-m", message)
    repo.git.push("origin", branch)


class Storage:
    def add_dir(self):
        raise NotImplementedError

    def remove_dir_with_name(self):
        raise NotImplementedError

    def remove_dir_with_path(self):
        raise NotImplementedError


class GithubStorage(Storage):
    """class representing Github Storage

    This storage create, update, and delete github repo and files

    Args:
        org (str, optional): github organization name
        token (str, optional): github oauth token
        username (str, optional): github username
        email (str, optional): github linked email

    """

    def __init__(
        self,
        org: str = None,
        token: str = None,
        username: str = None,
        email: str = None,
    ):
        self.org_name = _get_value(org, "GITHUB_ORG")
        self.token = _get_value(token, "GITHUB_TOKEN")
        self._username = _get_value(username, "GITHUB_USERNAME", optional=True)
        self._email = _get_value(email, "GITHUB_EMAIL", optional=True)
        self.org = Github(self.token).get_organization(self.org_name)

    @property
    def username(self):
        if not self._username:
            raise RuntimeError(
                "Please set usename attr or env variable GITHUB_USERNAME."
            )
        return self._username

    @property
    def email(self):
        if not self._email:
            raise RuntimeError("Please set email attr or env variable GITHUB_EMAIL.")
        return self._email

    def _init_local_repo(self, path: Path, remote_url: str):
        repo = Repo.init(path)
        repo = setup_auth_for_new_repo(repo, self.org_name, self.token, remote_url)
        repo.config_writer().set_value("user", "name", self.username).release()
        repo.config_writer().set_value("user", "email", self.email).release()
        return repo

    def _init_remote_repo(self, name: str, description: str):
        """Creates remote repo in Github and returns it's url."""

        repo = self.org.create_repo(name)
        time.sleep(2)
        return repo._html_url.value

    def add_dir(self, path: Path, description: str):
        """dir local dir to github."""
        remote_repo_url = self._init_remote_repo(
            name=path.name, description=description
        )
        local_repo = self._init_local_repo(path=path, remote_url=remote_repo_url)
        commit_and_push(repo=local_repo, message="Initial commit")
        return local_repo

    def remove_dir_with_name(self, name: str):
        repo = self.org.get_repo(name)
        repo.delete()

    def remove_dir_with_path(self, path: Path):
        """Remove repo with local path, assumes that local and remote name is same."""
        repo = self.org.get_repo(path.name)
        repo.delete()
        shutil.rmtree(str(path))

    def get_dir_with_name(self, name: str):
        repo = self.org.get_repo(name)
        return repo

    def get_dir_with_path(self, path: Path):
        repo = self.org.get_repo(path.name)
        return repo

    def add_file(
        self, dir_name: str, path: str, content: str, message: str, update=False
    ):
        """add file to `name` repo.

        Args:
            dir_name: name of repo to add file to.
            path: path to add the file.
            content: content of the file.
            message: git commit message.
        """

        repo = self.org.get_repo(dir_name)
        if update:
            old_content = repo.get_contents(path)
            repo.update_file(old_content.path, message, content, old_content.sha)
        else:
            repo.create_file(path, message, content)

    def get_file(self, dir_name, path: str, branch="master"):
        repo = self.org.get_repo(dir_name)
        contents = repo.get_contents(path, ref=branch)
        return contents

    def remove_file(
        self, dir_name: str, path: str, message: str, branch: str = "master"
    ):
        repo = self.org.get_repo(dir_name)
        contents = repo.get_contents(path, ref=branch)
        repo.delete_file(contents.path, message, contents.sha, branch=branch)
