import os
import requests
import base64
import re
from git import Repo
from pathlib import Path
from tqdm import tqdm


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
        tree_entry = [t for t in data['tree'] if t['path'] == 'README.md'][0]  # find the README to get its URL

        return tree_entry['url']

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
    def get_work_id_column(decoded_blob):
        """
        Get the work_id from the decoded blob and return a list of work_id
        """
        work_id = re.compile(r"\[P[0-9]{6}\]").findall(decoded_blob)

        return work_id

    @staticmethod
    def cleanup_work_id_list(list):
        """
        Remove the brackets from [PXXXXXX] for every work_id
        """
        work_ids = [s.replace("[", "").replace("]", "") for s in list]

        return work_ids

    def get_list_of_poti(self):
        """
        Getting the full list of poti based on the openpecha-catalog
        The catalog is too big to get the whole content through normal github API.
        It's necessary to get the blob through the Git Data API, for that we need the files
        hash or URL
        """
        collection_blob_url = self.get_collection_blob_url()
        blob_content = self.get_blob_content(collection_blob_url)
        decoded_blob = self.decode_bas64_blob(blob_content)

        work_id_column = self.get_work_id_column(decoded_blob)
        cleaned_list = self.cleanup_work_id_list(work_id_column)

        return cleaned_list

    def pull_latest_master_commit(self, work_id):
        """
        Takes a work_id as a parameter and pulls the latest commit on the master branch
        """
        repo = Repo(str(Path(self.local_dir, work_id)))
        repo.heads['master'].checkout()
        repo.remotes.origin.pull()

    def clone_poti(self, work_id):
        """
        Given a work_id, clones the repo from openpecha to self.local_dir
        """
        Repo.clone_from(f"{self.openpecha_git}/{work_id}.git", str(Path(self.local_dir,work_id)))

    def has_been_cloned(self, work_id):
        """
        Check if work_id has already been cloned by looking if there is
        a folder with the work_id name in the local directory
        """
        path = Path(self.local_dir,work_id)
        return path.is_dir()

    def clone_or_pull_poti(self, work_id):
        if self.has_been_cloned(work_id):
            self.pull_latest_master_commit(work_id)
        else:
            self.clone_poti(work_id)

    def get_all_poti(self):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.local_dir
        """
        for poti in tqdm(self.get_list_of_poti()):
            self.clone_or_pull_poti(poti)

