import pytest

from openpecha.utils import download_pecha


@pytest.mark.skip("Downloading github repo")
def test_download_pecha():
    pecha_path = download_pecha("collections")
