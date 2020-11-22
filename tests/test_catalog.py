import pytest

from openpecha.catalog.manager import CatalogManager
from openpecha.formatters import *


@pytest.mark.skip(reason="no urgent")
def test_googleocr():
    catalog = CatalogManager(
        formatter=GoogleOCRFormatter(), last_id_fn="ocr-machine-08_last_id"
    )
    catalog.ocr_to_opf("./tests/data/formatter/google_ocr/W00001")
    catalog.update_catalog()


@pytest.mark.skip(reason="no urgent")
def test_hfml_with_metadata():
    metadata = {
        "source_metadata": {
            "title": "example-title",
            "subtitle": "v001",
            "author": "authors",
            "id": "2323",
        }
    }
    layers = ["Citation", "BookTitle", "Author"]
    catalog = CatalogManager(
        formatter=HFMLFormatter(output_path="./output", metadata=metadata),
        layers=layers,
    )
    catalog.add_hfml_item("./tests/data/formatter/hfml/P0001")
    catalog.update()


if __name__ == "__main__":
    test_hfml_with_metadata()
