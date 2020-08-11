from pathlib import Path

from openpecha.serializers import EpubSerializer, SerializeHFML, SerializeMd
from openpecha.serializers.serialize import Serialize

# import pytest


# For testing read_base_layer, add_chars and apply_layer
# @pytest.fixture(scope="module")
# def opf_path():
#     opf_path = "tests/data/W1OP000001/W1OP000001.opf"
#     return opf_path


# Test HFML Serializer
hfml_opf_path = Path("tests/data/serialize_test/hfml/hfml.opf")

# def test_hfml_serializer():
#     opf_path = 'tests/data/serialize/hfml/P000001/P000001.opf'
#     text_id = 'T1'
#     layers = ['pagination']

#     serializer = SerializeHFML(opf_path, text_id, layers)
#     serializer.apply_layers()
#     result = serializer.get_result()
#     print(result)


def test_hfml_serializer_tsadra():
    opf_path = Path("./tests/data/serialize/tsadra/P000001/P000001.opf")
    pecha_id = "P000001"
    serializer = EpubSerializer(opf_path)
    serializer.apply_layers()
    serializer.serilize(pecha_id)


if __name__ == "__main__":
    # test_hfml_serializer()
    opf_path = Path("./test_opf/P000001/P000001.opf")
    pecha_id = "P000001"
    serializer = EpubSerializer(opf_path)
    serializer.apply_layers()
    serializer.serilize(pecha_id)
