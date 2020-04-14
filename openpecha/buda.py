import os
import requests
import base64
import re
from git import Repo
from pathlib import Path
from tqdm import tqdm
import urllib.request
from urllib.error import HTTPError
import traceback
from inspect import currentframe, getframeinfo

from openpecha.errors import Error


class OpenPecha:
    def __init__(self, local_dir=str(Path.home()/'.openpecha/data')):
        self.catalog_url = "https://api.github.com/repos/OpenPecha/openpecha-catalog/git/trees/master"
        self.openpecha_git = "https://github.com/OpenPecha"
        self.local_dir = local_dir
        if not Path(local_dir).is_dir():
            Path(local_dir).mkdir(parents=True)

    def get_collection_blob_url(self):
        """
        Get the url for the README blob for the work collection
        """
        data = requests.get(url=self.catalog_url).json()  # getting the full repo
        try:
            tree_entry = [t for t in data['tree'] if t['path'] == 'README.md'][0]  # find the README to get its URL
            return tree_entry['url']
        except IndexError:
            Error(0, f"The README.md file not found at the root of the openpecha git\n```{traceback.format_exc()}```")

    @staticmethod
    def get_blob_content(blob_url):
        """
        Get the blob content from the url provided in parameter
        """
        base64_content = requests.get(blob_url).json()['content']

        return base64_content

    @staticmethod
    def decode_bas64_blob(base64_blob):
        """
         Decode the base64 encoded blob into UTF-8
        """
        decoded_list_data = base64.b64decode(base64_blob).decode("utf-8")

        return decoded_list_data

    @staticmethod
    def get_op_lname_column(decoded_blob):
        """
        Get the op_lname from the decoded blob and return a list of op_lname
        """
        op_lname = re.compile(r"\[P[0-9]{6}\]").findall(decoded_blob)

        return op_lname

    @staticmethod
    def cleanup_op_lname_list(collection):
        """
        Remove the brackets from [PXXXXXX] for every op_lname
        """
        op_lnames = [s.replace("[", "").replace("]", "") for s in collection]

        return op_lnames

    def get_list_of_poti(self):
        """
        Getting the full list of poti based on the openpecha-catalog
        The catalog is too big to get the whole content through normal github API.
        It's necessary to get the blob through the Git Data API, for that we need the files
        hash or URL
        """
        collection_blob_url = self.get_collection_blob_url()
        if collection_blob_url:
            blob_content = self.get_blob_content(collection_blob_url)
            decoded_blob = self.decode_bas64_blob(blob_content)

            op_lname_column = self.get_op_lname_column(decoded_blob)
            cleaned_list = self.cleanup_op_lname_list(op_lname_column)

            return cleaned_list

    def pull_latest_master_commit(self, op_lname):
        """
        Takes a op_lname as a parameter and pulls the latest commit on the master branch
        """
        repo = Repo(str(Path(self.local_dir, op_lname)))
        repo.heads['master'].checkout()
        repo.remotes.origin.pull()

    def clone_poti(self, op_lname):
        """
        Given a op_lname, clones the repo from openpecha to self.local_dir
        """
        Repo.clone_from(f"{self.openpecha_git}/{op_lname}.git", str(Path(self.local_dir,op_lname)))

    def has_been_cloned(self, op_lname):
        """
        Check if op_lname has already been cloned by looking if there is
        a folder with the op_lname name in the local directory
        """
        path = Path(self.local_dir, op_lname)
        return path.is_dir()

    def clone_or_pull_poti(self, op_lname):
        if self.has_been_cloned(op_lname):
            self.pull_latest_master_commit(op_lname)
        else:
            self.clone_poti(op_lname)

    def poti_git_exists(self, op_lname):
        """
        Test if the op_lname has a corresponding git in self.openpecha_git
        """
        url = f"{self.openpecha_git}/{op_lname}.git"
        try:
            return urllib.request.urlopen(url).getcode()
        except HTTPError:
            Error(0, f"Poti _{op_lname}_ is not present on the openpecha git: {url}")

    def get_all_poti(self):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.local_dir
        """
        for poti in tqdm(self.get_list_of_poti()):
            if self.poti_git_exists(poti) == 200:
                self.clone_or_pull_poti(poti)


