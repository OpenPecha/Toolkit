from pathlib import Path

import pytest

from openpoti.serialize import Serialize
from openpoti.serializemd import SerializeMd


# For testing read_base_layer, add_chars and apply_layer
@pytest.fixture(scope='module')
def opf_path():
    opf_path = './data/W1OP000001/W1OP000001.opf'
    return opf_path

# # Test case for get_result on muttiple OpenPoi
# def get_opf_paths():
#     DATA_PATH = './data'
#     opf_paths = []
#     for op_name in ['W1OP000001', 'W1OP000198']:
#         opf_paths.append({
#             'op': op_name,
#             'opf_path': f'{DATA_PATH}/{op_name}/{op_name}.opf'
#         })
#     return opf_paths
    
# @pytest.fixture(params=get_opf_paths())
# def opf_path_test_cases(request):
#     request.param
    

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


@pytest.fixture(scope='module')
def get_result_opf_path():
    opf_path = './data/W1OP000198/W1OP000198.opf'
    return opf_path

def test_get_result(get_result_opf_path):
    serializer_title = SerializeMd(get_result_opf_path)
    serializer_yigchung = SerializeMd(get_result_opf_path)
    serializer_quotes = SerializeMd(get_result_opf_path)
    serializer_sapche = SerializeMd(get_result_opf_path)
    Serializer = SerializeMd(get_result_opf_path)

    serializer_title.apply_layer('title')
    serializer_yigchung.apply_layer('yigchung')
    serializer_quotes.apply_layer('quotes')
    serializer_sapche.apply_layer('sapche')
    Serializer.apply_layers()

    result_title = serializer_title.get_result()
    result_yigchung = serializer_yigchung.get_result()
    result_quotes = serializer_quotes.get_result()
    result_sapche = serializer_sapche.get_result()
    result = Serializer.get_result()

    expected_result_title = Path('data/serialize_test/W1OP000198/title_expected.txt').read_text()
    expected_result_yigchung = Path('data/serialize_test/W1OP000198/yigchung_expected.txt').read_text()
    expected_result_quotes = Path('data/serialize_test/W1OP000198/quotes_expected.txt').read_text()
    expected_result_sapche = Path('data/serialize_test/W1OP000198/sapche_expected.txt').read_text()
    expected_result = Path('data/serialize_test/W1OP000198/all_expected.txt').read_text()

    assert result_title == expected_result_title
    assert result_yigchung == expected_result_yigchung
    assert result_quotes == expected_result_quotes
    assert result_sapche == expected_result_sapche
    assert result == expected_result