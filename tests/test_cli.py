import pytest

from openpecha.cli import download_pecha


@pytest.mark.skip
def test_download_pecha():
    pecha_path = download_pecha("P000792")
    print(pecha_path)


if __name__ == "__main__":
    test_download_pecha()
