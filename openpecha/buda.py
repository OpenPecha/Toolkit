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

    def get_decoded_list_data(self, collection_blob_url):
        """
         Get the full content of the README blob and decode it from base64 to utf-8
        """
        
        base64_content = requests.get(collection_blob_url).json()['content']
        decoded_list_data = base64.b64decode(base64_content).decode("utf-8")  # decode the base64 in UTF-8

        return decoded_list_data

    def cleanup_work_id_list(self, list):
        """
        Remove the brackets from [PXXXXXX] for every work_id
        """

        return [s.replace("[", "").replace("]", "") for s in list]


    def get_list_of_poti(self):
        """
        Getting the full list of poti based on the openpecha-catalog
        The catalog is too big to get the whole content through normal github API.
        It's necessary to get the blob through the Git Data API, for that we need the files
        hash or URL
        """

        collection_blob_url = self.get_collection_blob_url()
        decoded_list_data = self.get_decoded_list_data(collection_blob_url)

        work_id = re.compile(r"\[P[0-9]{6}\]").findall(decoded_list_data)
        cleaned_list = self.cleanup_work_id_list(work_id)

        return cleaned_list
