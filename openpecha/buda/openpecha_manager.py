import requests
import base64
import re
from pathlib import Path
from tqdm import tqdm
import traceback

from openpecha.buda.errors import Error
from openpecha.buda.openpecha_git import OpenpechaGit
from openpecha.serializers.rdf import Rdf


class OpenpechaManager:
    def __init__(self, local_dir=str(Path.home()/'.openpecha/data')):
        self.openpecha_api = "https://api.github.com/repos/OpenPecha"
        self.openpecha_git = "https://github.com/OpenPecha"
        self.local_dir = local_dir
        if not Path(local_dir).is_dir():
            Path(local_dir).mkdir(parents=True)

    def get_collection_blob_url(self):
        """
        Get the url for the README blob for the work collection.

        TODO: maybe a csv file should be fetched instead?

        TODO: we should use a local repo that we pull instead of the github api directly (less urgent)
        """
        catalog_url = f'{self.openpecha_api}/openpecha-catalog/git/trees/master'
        data = requests.get(url=catalog_url).json()  # getting the full repo
        try:
            tree_entry = [t for t in data['tree'] if t['path'] == 'README.md'][0]  # find the README to get its URL
            return tree_entry['url']
        except IndexError:
            Error(IndexError, f"The README.md file not found at the root of the openpecha git\n```{traceback.format_exc()}```")

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

    def get_all_poti(self):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.local_dir
        """
        for poti in tqdm(self.get_list_of_poti(), ascii=True, desc='Cloning or pulling the poti'):
            op = OpenpechaGit(poti)
            if op.poti_git_exists() == 200:
                op.clone_or_pull_poti()

    def transform_all_in_rdf(self):
        self.get_all_poti()
        for local_poti in tqdm(self.get_list_of_poti(), ascii=True, desc='Converting into rdf'):
            rdf_poti = Rdf(local_poti)
            rdf_poti.set_instance()
            """
            Now you can access the rdf content with rdf_poti.print_rdf() or return the lod_g with rdf_poti.lod_g() to 
            send it to your database
            """




