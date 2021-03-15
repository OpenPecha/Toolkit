import base64
import logging
from abc import ABC, abstractclassmethod

import requests
from github import Github

from .config import GITHUB_BUCKET_CONFIG
from .utils import create_pecha_id


class Bucket(ABC):
    """A class representing a Bucket on Cloud Storage."""

    def __init__(self, name, config):
        self.name = name
        self.config = config
        super().__init__()

    @abstractclassmethod
    def _get_client(self, name, token):
        pass

    @abstractclassmethod
    def get_pecha_base(self, id):
        pass

    @abstractclassmethod
    def get_all_pechas_base(self):
        pass


class GithubBucket(Bucket):
    def __init__(self, name, config=GITHUB_BUCKET_CONFIG):
        self.client = self._get_client(name, config["token"])
        super().__init__(name, config)

    def _get_client(self, name, token):
        """Return github org object"""
        g = Github(token)
        org = g.get_organization(name)
        return org

    @staticmethod
    def get_blob_content(blob_url):
        """
        Get the blob content from the url provided in parameter
        """
        base64_content = requests.get(blob_url).json()["content"]
        return base64_content

    @staticmethod
    def decode_bas64_blob(base64_blob):
        """
        Decode the base64 encoded blob into UTF-8
        """
        decoded_list_data = base64.b64decode(base64_blob).decode("utf-8")
        return decoded_list_data

    def _get_content(self, gh_file_obj):
        blob_content = self.get_blob_content(gh_file_obj.git_url)
        decoded_blob = self.decode_bas64_blob(blob_content)
        return decoded_blob

    def get_pecha_base(self, id):
        try:
            repo = self.client.get_repo(id)
        except Exception:
            return [], ""
        for vol_base_file_obj in repo.get_contents(f"{id}.opf/base"):
            vol_base_content = self._get_content(vol_base_file_obj)
            logging.info(f"Downloaded {vol_base_file_obj.name}")
            yield vol_base_content, vol_base_file_obj.name

    def get_all_pechas_base(self):
        for pecha_num in range(
            self.config["catalog"]["start_id"], self.config["catalog"]["end_id"] + 1
        ):
            pecha_id = create_pecha_id(pecha_num)
            logging.info(f"Downloading {pecha_id}")
            yield pecha_id, self.get_pecha_base(pecha_id)
