import enum
import os
import shutil
import time
from pathlib import Path

from git import Repo
from github import Github


class Publishers(enum.Enum):
    GITHUB = enum.auto()


def get_publishers(publishers=[], all=False):
    if all:
        publishers = list(Publishers)
    prepared_publishers = {}
    for pub in publishers:
        if pub == Publishers.GITHUB:
            prepared_publishers[pub] = GithubPublisher()
    return prepared_publishers


def _getenv(name):
    try:
        env = os.environ[name]
    except KeyError:
        raise RuntimeError(f"Please set {name} environment variable")
    return env


def _get_value(value, env_name):
    return value if value else _getenv(env_name)


def commit_and_push(repo, message, branch="master"):
    repo.git.add("-A")
    repo.git.commit("-m", message)
    repo.git.push("origin", branch)


class PublisherBase:
    def publish(self):
        raise NotImplementedError

    def remove(self):
        raise NotImplementedError


class GithubPublisher(PublisherBase):
    """class representing Github publisher

    This publisher creates local openpecha a git repo
    and in remote github

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
        self.org = _get_value(org, "GITHUB_ORG")
        self.token = _get_value(token, "GITHUB_TOKEN")
        self.username = _get_value(username, "GITHUB_USERNAME")
        self.email = _get_value(email, "GITHUB_EMAIL")
        self._org = Github(self.token).get_organization(self.org)

    def _init_local_repo(self, path: Path, remote_url: str):
        repo = Repo.init(path)
        old_url = remote_url.split("//")
        auth_remote_url = f"{old_url[0]}//{self.org}:{self.token}@{old_url[1]}"
        repo.create_remote("origin", auth_remote_url)

        repo.config_writer().set_value("user", "name", self.username).release()
        repo.config_writer().set_value("user", "email", self.email).release()
        return repo

    def _init_remote_repo(self, name: str, description: str):
        """Creates remote repo in Github and returns it's url."""

        repo = self.org.create_repo(name)
        time.sleep(2)
        return repo._html_url.value

    def publish(self, path: Path, description: str):
        """publish openpecha to github."""
        remote_repo_url = self._init_remote_repo(
            name=path.name, description=description
        )
        local_repo = self._init_local_repo(path=path, remote_url=remote_repo_url)
        commit_and_push(repo=local_repo, message="Initial commit")

    def remove(self, name: str, path: Path = None):
        repo = self.org.get_repo(name)
        repo.delete()
        if path:
            shutil.rmtree(str(path))
