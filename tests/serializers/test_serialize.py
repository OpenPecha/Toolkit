import tempfile
from pathlib import Path

import pytest
from yaml import serialize

from openpecha.serializers import EditorSerializer, EpubSerializer, HFMLSerializer


# For testing read_base_layer, add_chars and apply_layer
@pytest.fixture(scope="module")
def opf_path():
    return Path("./tests/data/serialize/tsadra/P000100.opf")


# Test HFML Serializer
# hfml_opf_path = Path("tests/data/serialize_test/hfml/hfml.opf")


# @pytest.mark.skip(reason="not important")
def test_hfml_serializer():
    opf_path = "./tests/data/serialize/hfml/opf/P000003.opf/"
    serializer = HFMLSerializer(opf_path)
    serializer.apply_layers()
    hfml_results = serializer.get_result()
    expected_hfml_vol1 = Path('./tests/data/serialize/hfml/expected_hfml/P000003/v001.txt').read_text(encoding='utf-8')
    expected_hfml_vol2 = Path('./tests/data/serialize/hfml/expected_hfml/P000003/v002.txt').read_text(encoding='utf-8')
    assert hfml_results['v001'] == expected_hfml_vol1
    assert hfml_results['v002'] == expected_hfml_vol2


def test_hfml_2_tsadra_serializer(opf_path):
    # with tempfile.TemporaryDirectory() as tmpdirname:
    tmpdirname = './'
    serializer = EpubSerializer(opf_path)
    out_fn = serializer.serialize(output_path=tmpdirname)
    assert Path(out_fn).name == "P000100.epub"
    Path('./P000100.epub').unlink()


def test_editor_serializer():
    opf_path = "./tests/data/serialize/tsadra/P000801/P000801.opf"
    expected_output = Path(
        "./tests/data/serialize/tsadra/editor_serializer_output.html"
    ).read_text(encoding="utf-8")
    serializer = EditorSerializer(opf_path)
    for base_name, result in serializer.serialize():
        assert base_name
        assert result == expected_output
