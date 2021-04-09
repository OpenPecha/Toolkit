import json
import tempfile
from pathlib import Path

import pytest

from openpecha.formatters import GoogleOCRFormatter


@pytest.fixture(scope="module")
def get_resources():
    data_path = Path("tests/data/formatter/google_ocr/W0001/I1PD95846")
    responses = [
        (json.load(fn.open()), fn.stem) for fn in sorted(list((data_path).iterdir()))
    ]
    formatter = GoogleOCRFormatter()
    return formatter, data_path, responses


def test_get_base_text(get_resources):
    formatter, data_path, responses = get_resources
    formatter.build_layers(responses, "I1PD95846")

    result = formatter.get_base_text()

    assert result

    # TODO: create base-text
    # expected = (data_path/'v001.txt').read_text()
    # assert result == expected


def test_build_layers(get_resources):
    formatter, data_path, responses = get_resources

    result = formatter.build_layers(responses, "I1PD95846")

    expected = {"pages": [(0, 19), (24, 888), (893, 1607), (1612, 1809)]}

    for result_page, expected_page in zip(result["pages"], expected["pages"]):
        assert result_page[:2] == expected_page


def test_with_gzip_json():
    ocr_path = Path("tests/data/formatter/google_ocr/W1PD95844")
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        pecha_path = formatter.create_opf(ocr_path, 1)
        assert isinstance(pecha_path, Path) and pecha_path.is_dir()
