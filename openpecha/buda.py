import requests
import base64
import re


class OpenPecha:
    def __init__(self):
        self.url = "https://api.github.com/repos/OpenPecha/openpecha-catalog/git/trees/master"

    def get_collection_blob_url(self):
        """
        Get the url for the README blob for the work collection
        """

        data = requests.get(url=self.url).json()  # getting the full repo
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

