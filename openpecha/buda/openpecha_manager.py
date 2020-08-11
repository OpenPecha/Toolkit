import base64
import codecs
import csv
import glob
import json
import logging
import os
import re
import traceback
from contextlib import closing
from pathlib import Path

import requests
from tqdm import tqdm

from openpecha.buda.errors import Error
from openpecha.buda.openpecha_git import OpenpechaGit
from openpecha.serializers.rdf import Rdf


class OpenpechaManager:
    def __init__(self, cache_dir=str(Path.home() / ".cache" / "openpecha")):
        self.openpecha_api = "https://api.github.com/repos/OpenPecha"
        self.openpecha_git = "https://github.com/OpenPecha"
        self.cache_dir = cache_dir
        self.commits = None
        if not Path(cache_dir).is_dir():
            Path(cache_dir).mkdir(parents=True)

    def get_collection_blob_url(self):
        """
        Get the url for the README blob for the work collection.

        TODO: maybe a csv file should be fetched instead?

        TODO: we should use a local repo that we pull instead of the github api directly (less urgent)
        """
        catalog_url = f"{self.openpecha_api}/openpecha-catalog/git/trees/master"
        data = requests.get(url=catalog_url).json()  # getting the full repo
        try:
            tree_entry = [t for t in data["tree"] if t["path"] == "README.md"][
                0
            ]  # find the README to get its URL
            return tree_entry["url"]
        except IndexError:
            Error(
                IndexError,
                f"The README.md file not found at the root of the openpecha git\n```{traceback.format_exc()}```",
            )

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

    def get_list_of_pecha(self):
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

    def fetch_all_pecha(self):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.cache_dir
        """
        for lname in tqdm(
            self.get_list_of_pecha(), ascii=True, desc="Cloning or pulling the pecha"
        ):
            self.fetch_pecha(lname)

    def fetch_pecha(self, lname):
        """
        Getting one pecha from the list and either cloning them or pulling to the latest commit.
        """
        opg = OpenpechaGit(lname, cache_dir=self.cache_dir)
        try:
            opg.get_repo(dst_sync=True)
        except Exception:
            logging.error("error fetching %s", lname)

    def get_local_poti_info(self, get_commit=True):
        """
        Getting all the poti from the list and either cloning them or pulling to the latest commit.
        All the repo are going to be stored in a local directory set by self.cache_dir
        """
        res = {}
        for d in glob.glob(self.cache_dir + "/*"):
            lname = os.path.basename(d)
            if not lname.startswith("P"):
                continue
            res[lname] = {}
            if get_commit:
                opg = OpenpechaGit(lname, cache_dir=self.cache_dir)
                rev = opg.get_local_latest_commit()
                res[lname]["rev"] = rev
        return res

    @staticmethod
    def fetch_op_commits(ldspdibaseurl="http://ldspdi.bdrc.io/"):
        """
        Fetches the list of all openpecha commits on BUDA
        """
        res = {}
        headers = {"Accept": "text/csv"}
        params = {"format": "csv"}
        with closing(
            requests.get(
                ldspdibaseurl + "/query/table/OP_allCommits",
                stream=True,
                headers=headers,
                params=params,
            )
        ) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), "utf-8"))
            for row in reader:
                if not row[0].startswith("http://purl.bdrc.io/resource/IE0OP"):
                    Error("store", "cannot interpret csv line starting with " + row[0])
                    continue
                res[row[0][34:]] = row[1]
        return res

    def get_buda_op_commits(self, ldspdibaseurl, force=False):
        if self.commits is not None and not force:
            return self.commits
        path = Path(self.cache_dir, "buda-commits.json")
        if path.is_file() and not force:
            with open(path) as json_file:
                self.commits = json.load(json_file)
                return self.commits
        commits = self.fetch_op_commits(ldspdibaseurl)
        with open(path, "w") as outfile:
            json.dump(commits, outfile)
        self.commits = commits
        return commits

    def set_commit(self, oplname, rev):
        if self.commits is None:
            logging.warn("updating op_commits without fetching commits first")
            return
        self.commits[oplname] = rev

    def write_commits(self):
        if self.commits is None:
            logging.warn("not writing None commits")
            return
        path = Path(self.cache_dir, "buda-commits.json")
        with open(path, "w") as outfile:
            json.dump(self.commits, outfile)

    @staticmethod
    def send_model_to_store(model, graphuri, storeurl):
        logging.info("sending %s to store", graphuri)
        ttlstr = model.serialize(format="turtle")
        headers = {"Content-Type": "text/turtle"}
        params = {"graph": graphuri}
        r = requests.put(storeurl, data=ttlstr, headers=headers, params=params)
        sc = r.status_code
        if (
            sc != requests.codes.ok
            and sc != requests.codes.created
            and sc != requests.codes.accepted
        ):
            Error("store", "The request to Fuseki returned code " + str(r.status_code))

    @staticmethod
    def write_model_debug(model, graphuri):
        lastslidx = graphuri.rfind("/")
        graphlname = graphuri[lastslidx + 1 :]
        fname = "/tmp/" + graphlname + ".ttl"
        model.serialize(destination=fname, format="turtle")

    def sync_cache_to_store(self, storeurl, ldspdibaseurl, force=False, idlist=None):
        buda_commits = {}
        if not force:
            buda_commits = self.get_buda_op_commits(ldspdibaseurl, force)
        for oplname, info in tqdm(
            self.get_local_poti_info(get_commit=(not force)).items(),
            ascii=True,
            desc="Converting into rdf",
        ):
            if idlist is not None and oplname not in idlist:
                continue
            if (
                force
                or (oplname not in buda_commits)
                or buda_commits[oplname] != info["rev"]
            ):
                # we need to sync this repo
                opgit = OpenpechaGit(oplname, cache_dir=self.cache_dir)
                op = opgit.get_openpecha()
                if op is None:
                    logging.error(
                        "skipping %s, can't get the openpecha object", oplname
                    )
                    continue
                if not op.is_ocr():
                    logging.info("skipping %s, not ocr", oplname)
                    continue
                rdf = Rdf(oplname, op)
                rdfgraph = rdf.get_graph()
                self.send_model_to_store(rdfgraph, str(rdf.graph_r), storeurl)
                # self.write_model_debug(rdfgraph, str(rdf.graph_r))
                self.set_commit(oplname, opgit.openpecharev)
            else:
                logging.info("skipping %s, already synced", oplname)
        self.write_commits()
