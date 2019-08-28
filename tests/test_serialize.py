import pytest
from openpoti.serialize import Serialize


@pytest.fixture(scope='module')
def serialize():
    op_path = 'usage/layer_output'
    test_op = 'W1OP000001'
    test_opf_path = f'{op_path}/{test_op}/{test_op}.opf'
    serialize = Serialize(test_opf_path)
    return serialize


def test_readbaselayer(serialize):
    assert isinstance(serialize.baselayer, str)