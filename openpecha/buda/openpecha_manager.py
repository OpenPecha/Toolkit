import requests
import base64
import re
from pathlib import Path
from tqdm import tqdm
import traceback
import csv
import json
import os
import glob
from contextlib import closing
import codecs

from openpecha.buda.errors import Error
from openpecha.buda.openpecha_git import OpenpechaGit
from openpecha.serializers.rdf import Rdf


class OpenpechaManager:
    def __init__(self, local_dir=str(Path.home()/'.cache'/'openpecha')):
        self.openpecha_api = "https://api.github.com/repos/OpenPecha"
        self.openpecha_git = "https://github.com/OpenPecha"
        self.local_dir = local_dir
        self.commits = None
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

    def fetch_all_poti(self):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.local_dir
        """
        for poti in tqdm(self.get_list_of_poti(), ascii=True, desc='Cloning or pulling the poti'):
            op = OpenpechaGit(poti, local_dir=self.local_dir)
            if op.poti_dstgit_exists() == 200:
                op.get_repo(dst_sync=True)
            return

    def get_local_poti_info(self):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.local_dir
        """
        res = {}
        for d in glob.glob(self.local_dir+"/*"):
            lname = os.path.basename(d)
            if not lname.startswith("P"):
                continue
            op = OpenpechaGit(lname, local_dir=self.local_dir)
            latest_local_commit = op.get_commit_to_sync()
            res[lname] = {"commit": latest_local_commit}
            return res
        return res

    @staticmethod
    def fetch_op_commits(ldspdibaseurl="http://ldspdi.bdrc.io/"):
        """
        Fetches the list of all openpecha commits on BUDA
        """
        res = {}
        headers = {'Accept': 'text/csv'}
        params = {'format': "csv"}
        with closing(requests.get(ldspdibaseurl+"/query/table/OP_allCommits", stream=True, headers=headers)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            for row in reader:
                if not row[0].startswith("http://purl.bdrc.io/resource/IE0OP"):
                    Error("store", "cannot interpret csv line starting with "+row[0])
                    continue
                res[row[0][34:]] = row[1]
        return res

    def get_buda_op_commits(self, ldspdibaseurl, force=False):
        if self.commits is not None and not force:
            return self.commits
        path = Path(self.local_dir, "buda-commits.json")
        if path.is_file() and not force:
            with open(path) as json_file:
                return json.load(json_file)
        commits = self.fetch_op_commits(ldspdibaseurl)
        with open(path, 'w') as outfile:
            json.dump(commits, outfile)
        self.commits = commits
        return commits

    @staticmethod
    def send_model_to_store(model, graphuri, storeurl):
        ttlstr = model.serialize(format="turtle")
        headers = {'Content-Type': 'text/turtle'}
        params = {'graph': graphuri}
        r = requests.put(storeurl, data=ttlstr, headers=headers, params=params)
        if r.status_code != requests.codes.ok:
            Error("store", "The request to Fuseki returned code "+str(r.status_code))

    @staticmethod
    def write_model_debug(model, graphuri):
        lastslidx = graphuri.rfind("/")
        graphlname = graphuri[lastslidx+1:]
        fname = "/tmp/"+graphlname+".ttl"
        g.serialize(destination=fname, format='turtle')

    def sync_cache_to_store(self, storeurl, ldspdibaseurl, force=False):
        self.get_local_poti_info()
        buda_commits = self.get_buda_op_commits(ldspdibaseurl, force)
        for oplname, info in tqdm(self.get_local_poti_info(), ascii=True, desc='Converting into rdf'):
            if (oplname not in buda_commits) or buda_commits[oplname] != info[commit]:
                # we need to sync this repo
                rdf_poti = Rdf(str(Path(local_dir, oplname)), from_git=True)
                rdf_poti.set_instance()
                #send_model_to_store(rdf_poti.lod_g(), rdf_poti.graph_uri, storeurl)
                write_model_debug(rdf_poti.lod_g(), rdf_poti.graph_uri)
            

