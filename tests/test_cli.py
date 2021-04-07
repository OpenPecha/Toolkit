import pytest

from openpecha.cli import download_pecha
from openpecha.buda.openpecha_manager import OpenpechaManager


@pytest.mark.skip
def test_download_pecha():
    pecha_path = download_pecha("P000800", branch="review")
    print(pecha_path)

@pytest.mark.skip
def test_download_cat():
    opmgr = OpenpechaManager()
    print(opmgr.get_list_of_pecha())

if __name__ == "__main__":
    test_download_pecha()
    #test_download_cat()
