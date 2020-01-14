from pathlib import Path

import pytest

from openpecha.serializers import Serialize
from openpecha.serializers import SerializeMd
from openpecha.serializers import SerializeHFML


# For testing read_base_layer, add_chars and apply_layer
@pytest.fixture(scope='module')
def opf_path():
    opf_path = 'tests/data/W1OP000001/W1OP000001.opf'
    return opf_path


# Test HFML Serializer
hfml_opf_path = Path('tests/data/serialize_test/hfml/hfml.opf')

def test_hfml_serializer():
    opf_path = 'tests/data/serialize/hfml/P000001/P000001.opf'
    text_id = 'T1'
    layers = ['pagination']

    serializer = SerializeHFML(opf_path, text_id, layers)
    serializer.apply_layers()
    result = serializer.get_result()
    print(result)


if __name__ == "__main__":
    test_hfml_serializer()