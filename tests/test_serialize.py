from pathlib import Path

import pytest

from openpecha.serializers import EpubSerializer, SerializeHFML, SerializeMd


# For testing read_base_layer, add_chars and apply_layer
@pytest.fixture(scope="module")
def opf_path():
    return Path("./tests/data/serialize/tsadra/P000100.opf")


# Test HFML Serializer
# hfml_opf_path = Path("tests/data/serialize_test/hfml/hfml.opf")

# def test_hfml_serializer():
#     opf_path = 'tests/data/serialize/hfml/P000001/P000001.opf'
#     text_id = 'T1'
#     layers = ['pagination']

#     serializer = SerializeHFML(opf_path, text_id, layers)
#     serializer.apply_layers()
#     result = serializer.get_result()
#     print(result)


def test_hfml_2_tsadra_serializer(opf_path):
    serializer = EpubSerializer(opf_path)
    serializer.apply_layers()
    serializer.serialize()


if __name__ == "__main__":
    test_hfml_2_tsadra_serializer(Path("./tests/data/serialize/tsadra/P000100.opf"))
