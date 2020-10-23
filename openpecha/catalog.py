"""catalog module contains all the functionalities necessary for managin
the catalog. Functonalities includes:
    - Creating opfs from input text
    - Assiging ID to the new opf
    - Updating the catalog with new opfs

"""

import os

import requests
import yaml

from openpecha.formatters import *
from openpecha.github_utils import create_file, create_readme, github_publish
from openpecha.utils import *

buildin_pipes = {
    "input": {"ocr_result_input": ocr_result_input},
    "release": {"create_release_with_assets": create_release_with_assets},
}


class CatalogManager:
    """Manages the catalog"""

    def __init__(
        self,
        pipes=None,
        formatter=None,
        layers=[],
        org="OpenPecha",
        token=os.environ.get("GITHUB_TOKEN"),
        not_include_files=["releases"],
        last_id_fn="last_id",
    ):
        self.org = org
        self.token = token
        self.repo_name = "catalog"
        self.batch_path = "data/batch.csv"
        self.last_id_path = f"data/{last_id_fn}"
        self.batch = []
        self.last_id = self._get_last_id()
        self.formatter = formatter
        self.layers = layers
        self.not_include_files = not_include_files
        self.pipes = pipes if pipes else buildin_pipes

    def _get_last_id(self):
        """returns the id assigin to last opf pecha"""
        last_id_url = f"https://raw.githubusercontent.com/{self.org}/{self.repo_name}/master/{self.last_id_path}"
        r = requests.get(last_id_url)
        return int(r.content.decode("utf-8").strip()[1:])

    def _add_id_url(self, row):
        id = row[0]
        row[0] = f"[{id}](https://github.com/{self.org}/{id})"
        return row

    def update(self):
        """Updates the catalog csv to have new opf-pechas metadata"""
        # update last_id
        content = self.batch[-1][0].strip()
        create_file(
            self.repo_name,
            self.last_id_path,
            content,
            "update last id of Pecha",
            update=True,
            org=self.org,
            token=self.token,
        )

        # update last_id
        self.last_id = int(content[1:])

        # create batch.csv
        content = (
            "\n".join([",".join(row) for row in map(self._add_id_url, self.batch)])
            + "\n"
        )
        create_file(
            self.repo_name,
            self.batch_path,
            content,
            "create new batch",
            org=self.org,
            token=self.token,
        )
        print("[INFO] Updated the catalog")

        # reset the batch
        self.batch = []

    def _get_catalog_metadata(self, meta_fn):
        metadata = yaml.safe_load(meta_fn.open())
        catalog_metadata = [
            metadata["id"].split(":")[-1],
            metadata["source_metadata"].get("title"),
            metadata["source_metadata"].get("subtitle"),
            metadata["source_metadata"].get("author"),
            metadata["source_metadata"].get("id"),
        ]
        self.batch.append(catalog_metadata)
        create_readme(metadata["source_metadata"], self.formatter.pecha_path)

    def format_and_publish(self, path):
        """Convert input pecha to opf-pecha with id assigined"""
        self.last_id += 1
        self.formatter.create_opf(path, self.last_id)
        self._get_catalog_metadata(self.formatter.meta_fn)
        github_publish(
            self.formatter.pecha_path,
            not_includes=self.not_include_files,
            layers=self.layers,
            org=self.org,
            token=self.token,
        )
        return self.formatter.pecha_path

    def add_ocr_item(self, path):
        self._process(path, "ocr_result_input", "create_release_with_assets")

    def add_hfml_item(self, path):
        self._process(path, "ocr_result_input")

    def _process(self, path, input_method, release_method=None):
        print("[INFO] Getting input")
        raw_pecha_path = self.pipes["input"][input_method](path)
        print("[INFO] Convert Pecha to OPF")
        opf_pecha_path = self.format_and_publish(raw_pecha_path)
        if release_method:
            print("[INFO] Release OPF pecha")
            self.pipes["release"][release_method](opf_pecha_path)
