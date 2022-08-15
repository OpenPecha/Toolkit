import json
import tempfile
from pathlib import Path

import py
import pytest
from openpecha.formatters import google_ocr

from openpecha.formatters.google_ocr import GoogleOCRFormatter
from openpecha.utils import load_yaml, dump_yaml


@pytest.fixture(scope="module")
def get_resources():

    data_path = Path(__file__).parent / "data" / "W0001" / "I1PD95846"
    responses = [
        (json.load(fn.open()), fn.stem) for fn in sorted(list((data_path).iterdir()))
    ]
    formatter = GoogleOCRFormatter()
    return formatter, data_path, responses


@pytest.mark.skip(reason="bdrc api failing")
def test_get_base_text(get_resources):
    formatter, data_path, responses = get_resources
    formatter.build_layers(responses, "I1PD95846")

    result = formatter.get_base_text()
    assert result

    # TODO: create base-text
    # expected = (data_path/'v001.txt').read_text()
    # assert result == expected


@pytest.mark.skip(reason="bdrc api failing")
def test_build_layers(get_resources):
    formatter, data_path, responses = get_resources

    result = formatter.build_layers(responses, "I1PD95846")

    expected = {"pages": [(0, 19), (24, 887), (892, 1601), (1606, 1799)]}

    for result_page, expected_page in zip(result["pages"], expected["pages"]):
        assert result_page[:2] == expected_page


@pytest.mark.skip(reason="bdrc api failing")
def test_with_gzip_json():
    ocr_path = Path(__file__).parent / "data" / "W1PD95844"
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        pecha_path = formatter.create_opf(ocr_path, 1, meta_flag=False)
        assert isinstance(pecha_path, Path) and pecha_path.is_dir()


def test_language_layer_formatter():
    language_annotated_text = (Path(__file__).parent / "data" / "language_code_annotated_text.txt").read_text(encoding='utf-8')
    expected_layer = load_yaml((Path(__file__).parent / "data" / "expected_language_layer.yml"))
    google_ocr_formatter = GoogleOCRFormatter()
    language_layer = google_ocr_formatter.format_language_layer(language_annotated_text)
    for (_, expected_ann), (_, lang_ann) in zip(expected_layer['annotations'].items(), language_layer['annotations'].items()):
        del expected_ann['id']
        del lang_ann['id']
        assert expected_ann == lang_ann