"""catalog module contains all the functionalities necessary for managin
the catalog. Functonalities includes:
    - Creating opfs from input text
    - Assiging ID to the new opf
    - Updating the catalog with new opfs

"""

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
        formatter_type=None,
        not_include_files=["releases"],
        last_id_fn="last_id",
    ):
        self.repo_name = "openpecha-catalog"
        self.batch_path = "data/batch.csv"
        self.last_id_path = f"data/{last_id_fn}"
        self.batch = []
        self.last_id = self._get_last_id()
        self.FormatterClass = self._get_formatter_class(formatter_type)
        self.not_include_files = not_include_files
        self.pipes = pipes if pipes else buildin_pipes

    def _get_formatter_class(self, formatter_type):
        """Returns formatter class based on the formatter-type"""
        if formatter_type == "ocr":
            return GoogleOCRFormatter
        elif formatter_type == "tsadra":
            return TsadraFormatter

    def _get_last_id(self):
        """returns the id assigin to last opf pecha"""
        last_id_url = f"https://raw.githubusercontent.com/OpenPecha/openpecha-catalog/master/{self.last_id_path}"
        r = requests.get(last_id_url)
        return int(r.content.decode("utf-8").strip()[1:])

    def _add_id_url(self, row):
        id = row[0]
        row[0] = f"[{id}](https://github.com/OpenPecha/{id})"
        return row

    def update_catalog(self):
        """Updates the catalog csv to have new opf-pechas metadata"""
        # update last_id
        content = self.batch[-1][0].strip()
        create_file(
            self.repo_name,
            self.last_id_path,
            content,
            "update last id of Pecha",
            update=True,
        )

        # update last_id
        self.last_id = int(content[1:])

        # create batch.csv
        content = (
            "\n".join([",".join(row) for row in map(self._add_id_url, self.batch)])
            + "\n"
        )
        create_file(self.repo_name, self.batch_path, content, "create new batch")
        print("[INFO] Updated the OpenPecha catalog")

        # reset the batch
        self.batch = []

    def _get_catalog_metadata(self, pecha_path):
        meta_fn = pecha_path / f"{pecha_path.name}.opf/meta.yml"
        metadata = yaml.safe_load(meta_fn.open())
        catalog_metadata = [
            metadata["id"].split(":")[-1],
            metadata["source_metadata"]["title"],
            metadata["source_metadata"]["volume"],
            metadata["source_metadata"]["author"],
            metadata["source_metadata"]["id"],
        ]
        self.batch.append(catalog_metadata)
        create_readme(metadata["source_metadata"], pecha_path)

    def format_and_publish(self, path):
        """Convert input pecha to opf-pecha with id assigined"""
        formatter = self.FormatterClass()
        self.last_id += 1
        pecha_path = formatter.create_opf(path, self.last_id)
        self._get_catalog_metadata(pecha_path)
        github_publish(pecha_path, not_includes=self.not_include_files)
        return pecha_path

    def ocr_to_opf(self, path):
        self._process(path, "ocr_result_input", "create_release_with_assets")

    def _process(self, path, input_method, release_method):
        print("[INFO] Getting input")
        raw_pecha_path = self.pipes["input"][input_method](path)
        print("[INFO] Convert Pecha to OPF")
        opf_pecha_path = self.format_and_publish(raw_pecha_path)
        print("[INFO] Release OPF pecha")
        self.pipes["release"][release_method](opf_pecha_path)


if __name__ == "__main__":
    catalog = CatalogManager(formatter_type="ocr", last_id_fn="ocr-machine-08_last_id")
    catalog.ocr_to_opf("./tests/data/formatter/google_ocr/W3CN472")
    catalog.update_catalog()
