import pytest

from openpecha.catalog.manager import CatalogManager


@pytest.mark.skip(reason="external call")
def test_add_batch():
    catalog = CatalogManager()
    catalog.batch_path = "data/upload/test-batch.csv"
    catalog.batch = [["P000001", "", "", "", ""]]

    catalog.update()


if __name__ == "__main__":
    test_add_batch()
