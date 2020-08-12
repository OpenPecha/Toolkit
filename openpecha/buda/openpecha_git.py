import logging
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

import requests
from git import Repo

from openpecha.buda.errors import Error
from openpecha.buda.op_bare import OpenpechaBare

ENV = {"GIT_TERMINAL_PROMPT": "0"}


class OpenpechaGit:
    """
    The OpenpechaGit class is here to help manage and pull all the Openpecha objects and store them on a temporary local
    repository
    It is initiated with
    - The Openpecha lname
    - The local dir (by default stored in ~/.openpecha/data)
    - The remote git of Openpecha
    - If we want the bare repo or a working tree on the local branch (by default the bare repo to save some space)
    """

    def __init__(
        self,
        op_lname,
        cache_dir=str(Path.home() / ".cache" / "openpecha"),
        openpecha_dstgit="https://github.com/OpenPecha",
        bare=True,
    ):
        self.lname = op_lname
        self.cache_dir = cache_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self.openpecha_dstgit = f"{openpecha_dstgit}/{self.lname}.git"
        self.bare = bare
        self.repo = None
        self.synced = False
        self.openpecha = None
        self.openpecharev = None

    def get_repo(self, dst_sync=False):
        """
        gets the repo, sync with dst (Github) if parameter is true, otherwise just return the local repo
        """
        if self.repo is not None:
            if dst_sync and not self.synced:
                self.repo.git.fetch()
                self.synced = True
            return self.repo
        if not self.poti_localgit_exists():
            if dst_sync:
                self.clone()
                return self.repo
            return None
        self.repo = Repo(str(Path(self.cache_dir, self.lname)))
        if dst_sync and not self.synced:
            self.repo.git.fetch()
            self.synced = True
        return self.repo

    def clone(self):
        """
        Given a op_lname, clones the repo from openpecha to self.cache_dir
        """
        if self.poti_localgit_exists():
            return
        self.repo = Repo.clone_from(
            self.openpecha_dstgit,
            str(Path(self.cache_dir, self.lname)),
            env=ENV,
            bare=self.bare,
        )
        self.synced = True

    def poti_localgit_exists(self):
        """
        Check if self.lname has already been cloned by looking if there is
        a folder with the self.lname name in the local directory
        """
        path = Path(self.cache_dir, self.lname)
        return path.is_dir()

    def poti_dstgit_exists(self):
        """
        Test if the self.lname has a corresponding git in self.openpecha_dstgit
        """
        try:
            return urllib.request.urlopen(self.openpecha_dstgit).getcode()
        except HTTPError:
            Error(
                HTTPError,
                f"Poti _{self.lname}_ is not present on the openpecha git: {self.openpecha_dstgit}",
            )

    def get_local_latest_commit(self, dst_sync=False, branchname="master"):
        """
        get the commit to sync to BUDA: the latest tag, or the latest commit of the master branch
        """
        repo = self.get_repo(dst_sync)
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        if tags:
            return tags[-1].commit.hexsha
        try:
            return repo.commit(branchname).hexsha
        except Exception:
            logging.error("cannot find branch %s for %s", branchname, self.lname)
            return None

    def get_openpecha(self, rev=None):
        if rev is None:
            rev = self.get_local_latest_commit()
        if rev is None:
            return None
        if self.openpecha is not None and self.openpecharev == rev:
            return self.openpecha
        self.openpecha = OpenpechaBare(self.lname, repo=self.get_repo(), rev=rev)
        self.openpecharev = rev
        return self.openpecha
