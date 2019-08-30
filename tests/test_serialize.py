from pathlib import Path

import pytest

from openpoti.serialize import Serialize
from openpoti.serializemd import SerializeMd


@pytest.fixture(scope='module')
def opf_path():
    op_path = './data'
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
    serializer_title = SerializeMd(opf_path)
    serializer_yigchung = SerializeMd(opf_path)

    serializer_title.apply_layer('title')
    serializer_yigchung.apply_layer('yigchung')
    result_title = serializer_title.chars_toapply
    result_yigchung = serializer_yigchung.chars_toapply

    expected_result_title = {
        0: (['# '], []), 73: (['# '], []), 5122: (['# '], []), 13316: (['# '], []), 
        17384: (['# '], []), 23478: (['# '], []), 36047: (['# '], []), 51718: (['# '], []), 
        60869: (['# '], []), 82453: (['# '], []), 101537: (['# '], [])
    }

    expected_result_yigchung = {
        109468: (['*'], []), 109489: ([], ['*']), 
        109820: (['*'], []), 109958: ([], ['*'])
    }
    assert result_title == expected_result_title
    assert result_yigchung == expected_result_yigchung


def test_get_all_layer(opf_path):
    serializer = Serialize(opf_path)

    result = serializer.get_all_layer()
    
    assert result == ['title', 'yigchung']


def test_apply_layers(opf_path):
    serializer = SerializeMd(opf_path)

    serializer.apply_layers()
    result = serializer.chars_toapply

    expected_result = {
        0: (['# '], []), 73: (['# '], []), 5122: (['# '], []), 13316: (['# '], []), 
        17384: (['# '], []), 23478: (['# '], []), 36047: (['# '], []), 51718: (['# '], []), 
        60869: (['# '], []), 82453: (['# '], []), 101537: (['# '], []),
        109468: (['*'], []), 109489: ([], ['*']), 109820: (['*'], []), 109958: ([], ['*'])
    }
    assert result == expected_result


def test_get_result(opf_path):
    serializer_title = SerializeMd(opf_path)
    serializer_yigchung = SerializeMd(opf_path)
    Serializer = SerializeMd(opf_path)

    serializer_title.apply_layer('title')
    serializer_yigchung.apply_layer('yigchung')
    Serializer.apply_layers()

    result_title = serializer_title.get_result()
    result_yigchung = serializer_yigchung.get_result()
    result = Serializer.get_result()

    expected_result_title = Path('data/export/title_expected.txt').read_text()
    expected_result_yigchung = Path('data/export/yigchung_expected.txt').read_text()
    expected_result = Path('data/export/all_expected.txt').read_text()

    assert result_title == expected_result_title
    assert result_yigchung == expected_result_yigchung
    assert result == expected_result