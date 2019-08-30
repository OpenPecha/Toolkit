import pytest
from openpoti.serialize import Serialize
from openpoti.serializemd import SerializeMd


@pytest.fixture(scope='module')
def opf_path():
    op_path = 'usage/new_layer_output'
    test_op = 'W1OP000001'
    opf_path = f'{op_path}/{test_op}/{test_op}.opf'
    return opf_path


def test_read_base_layer(opf_path):
    serializer = Serialize(opf_path)

    result = serializer.baselayer

    assert isinstance(result, str)


def test_add_chars(opf_path):
    serializer = Serialize(opf_path)

    serializer.add_chars(0, True, '#')
    serializer.add_chars(10, True, '*')
    serializer.add_chars(20, False, '*')
    result = serializer.chars_toapply

    expected_result = {
        0: (['#'], []),
        10: (['*'], []),
        20: ([], ['*'])
    }
    assert result == expected_result


def test_apply_layer(opf_path):
    serializer = SerializeMd(opf_path)

    serializer.apply_layer('title')
    serializer.apply_layer('yigchung')
    print()
    print(serializer.chars_toapply)
    result = len(serializer.chars_toapply)

    assert result > 0