from pathlib import Path

import pytest

from openpecha.serializers import HFMLSerializer


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