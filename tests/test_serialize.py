from pathlib import Path

import pytest

from openpecha.serializers import EpubSerializer, HFMLSerializer, SerializeMd


# For testing read_base_layer, add_chars and apply_layer
@pytest.fixture(scope="module")
def opf_path():
    return Path("./tests/data/serialize/tsadra/P000100.opf")


# Test HFML Serializer
# hfml_opf_path = Path("tests/data/serialize_test/hfml/hfml.opf")


@pytest.mark.skip(reason="not important")
def test_hfml_serializer():

    opf_path = "./tests/data/serialize/hfml/P000002.opf/"
    output_path = "./output/P000002_hfml/"
    serializer = HFMLSerializer(opf_path)
    serializer.serialize(output_path=output_path)


def test_hfml_2_tsadra_serializer(opf_path):
    serializer = EpubSerializer(opf_path)
    serializer.apply_layers()
    out_fn = serializer.serialize()
    assert str(out_fn) == "output/epub_output/P000100.epub"
