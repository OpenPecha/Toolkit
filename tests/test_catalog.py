import tempfile

import pytest

from openpecha.catalog.manager import CatalogManager
from openpecha.formatters import *

metadata = {
    "source_metadata": {
        "title": "example-title",
        "subtitle": "v001",
        "author": "authors",
        "id": "2323",
    }
}


@pytest.mark.skip(reason="no urgent")
def test_googleocr():
    catalog = CatalogManager(
        formatter=GoogleOCRFormatter(), last_id_fn="ocr-machine-08_last_id"
    )
    catalog.ocr_to_opf("./tests/data/formatter/google_ocr/W00001")
    catalog.update_catalog()


@pytest.mark.skip(reason="no urgent")
def test_hfml_with_metadata():
    layers = ["Citation", "BookTitle", "Author"]
    catalog = CatalogManager(
        formatter=HFMLFormatter(output_path="./output", metadata=metadata),
        layers=layers,
    )
    catalog.add_hfml_item("./tests/data/formatter/hfml/P0001")
    catalog.update()


def get_fake_img():
    return tempfile.NamedTemporaryFile(delete=False, suffix=".png").name


@pytest.mark.skip(reason="creating github repo")
def test_create_emtpy_item():
    assets = {"image": [get_fake_img()]}
    catalog = CatalogManager(
        formatter=EmptyEbook(
            output_path="./output", metadata=metadata["source_metadata"], assets=assets
        ),
    )
    catalog.add_empty_item("this is text only")


if __name__ == "__main__":
    test_create_emtpy_item()
