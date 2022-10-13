"""catalog module contains all the functionalities necessary for managin
the catalog. Functonalities includes:
    - Creating opfs from input text
    - Assiging ID to the new opf
    - Updating the catalog with new opfs

"""

import yaml

from openpecha.core.ids import get_initial_pecha_id
from openpecha.github_utils import create_readme, github_publish
from openpecha.storages import GithubStorage, Storage
from openpecha.utils import create_release_with_assets, ocr_result_input
from openpecha.formatters.ocr.google_vision import GoogleVisionBDRCFileProvider

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
        not_include_files=["releases"],
        storage: Storage = None,
    ):
        self.repo_name = "catalog"
        self.batch_path = "data/batch.csv"
        self.batch = []
        self.formatter = formatter
        self.layers = layers
        self.not_include_files = not_include_files
        self.pipes = pipes if pipes else buildin_pipes
        self.storage = storage if storage else GithubStorage()

    def _add_id_url(self, row):
        id = row[0]
        row[0] = f"[{id}](https://github.com/{self.storage.org_name}/{id})"
        return row

    def update(self):
        """Updates the catalog csv to have new opf-pechas metadata"""
        content = (
            "\n".join([",".join(row) for row in map(self._add_id_url, self.batch)])
            + "\n"
        )
        self.storage.add_file(
            dir_name=self.repo_name,
            path=self.batch_path,
            content=content,
            message="update with new batch",
        )
        print("[INFO] Updated the catalog")

        # reset the batch
        self.batch = []

    def _get_catalog_metadata(self, meta_fn):
        metadata = yaml.safe_load(meta_fn.open())
        catalog_metadata = [
            metadata["id"].split(":")[-1],
            metadata["source_metadata"].get("title", ""),
            metadata["source_metadata"].get("subtitle", ""),
            metadata["source_metadata"].get("author", ""),
            metadata["source_metadata"].get("id", ""),
        ]
        self.batch.append(catalog_metadata)
        create_readme(metadata["source_metadata"], self.formatter.pecha_path)

    def format_and_publish(self, path, ocr_import_info):
        """Convert input pecha to opf-pecha with id assigined"""
        data_provider = GoogleVisionBDRCFileProvider(path.name, ocr_import_info, path, mode="local")
        self.formatter.create_opf(data_provider, None, {}, ocr_import_info)
        self._get_catalog_metadata(self.formatter.meta_fn)
        github_publish(
            self.formatter.pecha_path,
            not_includes=self.not_include_files,
            layers=self.layers,
            org=self.storage.org_name,
            token=self.storage.token,
        )
        return self.formatter.pecha_path

    def add_ocr_item(self, path, ocr_import_info):
        self._process(path, ocr_import_info, "ocr_result_input", "create_release_with_assets")

    def add_hfml_item(self, path):
        self._process(path, "ocr_result_input")

    def add_empty_item(self, text):
        self._process(text, "ocr_result_input")

    def _process(self, path, ocr_import_info, input_method, release_method=None):
        print("[INFO] Getting input")
        raw_pecha_path = self.pipes["input"][input_method](path)
        print("[INFO] Convert Pecha to OPF")
        opf_pecha_path = self.format_and_publish(raw_pecha_path, ocr_import_info)
        if release_method:
            print("[INFO] Release OPF pecha")
            self.pipes["release"][release_method](opf_pecha_path)
