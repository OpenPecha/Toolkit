from git import Repo
import urllib.request
import requests

from pathlib import Path
from urllib.error import HTTPError

from openpecha.buda.errors import Error


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
    def __init__(self, op_lname, local_dir=str(Path.home()/'.openpecha/data'),
                 openpecha_git="https://github.com/OpenPecha", bare=True):
        self.lname = op_lname
        self.local_dir = local_dir
        self.openpecha_git = f"{openpecha_git}/{self.lname}.git"
        self.openpecha_api = f"https://api.github.com/repos/OpenPecha/{self.lname}"
        self.bare = bare

    def fetch_latest_master_commit(self):
        """
        Takes a op_lname as a parameter and pulls the latest commit on the master branch
        """
        repo = Repo(str(Path(self.local_dir, self.lname)))
        repo.git.fetch()

    def clone_poti(self):
        """
        Given a op_lname, clones the repo from openpecha to self.local_dir
        """
        Repo.clone_from(self.openpecha_git, str(Path(self.local_dir, self.lname)), bare=self.bare)

    def has_been_cloned(self):
        """
        Check if self.lname has already been cloned by looking if there is
        a folder with the self.lname name in the local directory
        """
        path = Path(self.local_dir, self.lname)
        return path.is_dir()

    def clone_or_pull_poti(self):
        if self.has_been_cloned():
            self.fetch_latest_master_commit()
        else:
            self.clone_poti()

    def poti_git_exists(self):
        """
        Test if the self.lname has a corresponding git in self.openpecha_git
        """
        try:
            return urllib.request.urlopen(self.openpecha_git).getcode()
        except HTTPError:
            Error(HTTPError, f"Poti _{self.lname}_ is not present on the openpecha git: {self.openpecha_git}")

    def get_json_tags(self):
        """
        Get a list of all the tags as a json
        """
        op_tags_url = f'{self.openpecha_api}/git/refs/tags'
        tags_json = requests.get(url=op_tags_url).json()

        return tags_json

    def get_last_commit(self):
        """
        get a list of all the commits as a json
        """
        op_commits_url = f'{self.openpecha_api}/commits/master'
        commit_json = requests.get(url=op_commits_url).json()

        return commit_json['sha']

    def get_all_tags(self):
        """
        Get a json of all the tags in the repo of op_lname
        Return a dictionary in the following format {tag_name: commit_sha, tag_name: commit_sha, ...}
        """
        dic = {}
        tags_json = self.get_json_tags()
        for tag in tags_json:
            dic[tag['ref'].split("/")[-1]] = tag['object']['sha']
        return dic

    def get_tag_commit_sha(self, tag):
        """
         Get the commit_sha corresponding to the tag from the op_lname
        """
        all_tags_dic = self.get_all_tags()
        try:
            commit_sha = all_tags_dic[tag]
        except KeyError:
            Error(KeyError, f"Poti _{self.lname}_ doesn't have a tag {tag}\nThe tags are {all_tags_dic}")

        return commit_sha

    def checkout_to_commit(self, commit_sha):
        """
        Change the current poti to the commit_sha provided in parameters
        """
        repo = Repo(str(Path(self.local_dir, self.lname)))
        repo.git.checkout(commit_sha)

    def get_poti_latest_commit(self, tag=None, branch=None):
        """
        If no tag is provided get the latest master commit, otherwise get the commit corresponding to a tag

        TODO: handle the branch argument, getting the latest commit of the specified branch
        """
        self.clone_or_pull_poti()
        if tag:
            commit_sha = self.get_tag_commit_sha(tag)
        else:
            commit_sha = self.get_last_commit()

        return commit_sha
