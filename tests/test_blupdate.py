import pytest
from pathlib import Path
import yaml

from openpoti.blupdate import Blupdate


@pytest.fixture(params=[{'srcbl': 'abefghijkl', 'dstbl': 'abcdefgkl'}])  
def inputs(request):
    return request.param


@pytest.fixture(params=[{'expected_result': [(0,2,0), (2,5,2), (8,10,-1)]}])
def compute_cctv_test_cases(request):
    return request.param

def test_compute_cctv(inputs, compute_cctv_test_cases):
    updater = Blupdate(inputs['srcbl'], inputs['dstbl'])

    result = updater.cctv

    assert result == compute_cctv_test_cases['expected_result']


@pytest.fixture(params=[{'srcblcoord': 3, 
                         'expected_result': (2, True)},
                        {'srcblcoord': 7,
                         'expected_result': (1, False)},
                        {'srcblcoord': 9,
                         'expected_result': (-1, True)},
                        {'srcblcoord': 5,
                         'expected_result': (1, False)}])
def cctv_for_coord_test_cases(request):
    return request.param

def test_get_cctv_for_coord(inputs, cctv_for_coord_test_cases):
    updater = Blupdate(inputs['srcbl'], inputs['dstbl'])

    result = updater.get_cctv_for_coord(cctv_for_coord_test_cases['srcblcoord'])

    assert result == cctv_for_coord_test_cases['expected_result']


@pytest.fixture(params=[{'srcblcoord': 3, 
                         'expected_result': ('abe', 'fghi')},
                         {'srcblcoord': 7, 
                         'expected_result': ('fghi', 'jkl')}])
def get_context_test_cases(request):
    return request.param

def test_get_context(inputs, get_context_test_cases):
    updater = Blupdate(inputs['srcbl'], inputs['dstbl'], context_len=4)

    result = updater.get_context(get_context_test_cases['srcblcoord'])

    assert result == get_context_test_cases['expected_result']


@pytest.fixture(params=[{'context': ('fghi', 'jkl'),
                          'dstcoordestimate': 8,
                          'expected_result': 7},
                          {'context': ('ab', 'efgh'),
                          'dstcoordestimate': 4,
                          'expected_result': 4},
                          {'context': ('ghij', 'kl'),
                          'dstcoordestimate': 7,
                          'expected_result': 7}])
def dmp_find_test_cases(request):
    return request.param

def test_dmp_find(inputs, dmp_find_test_cases):
    updater = Blupdate(inputs['srcbl'], inputs['dstbl'], context_len=4)

    result = updater.dmp_find(dmp_find_test_cases['context'],
                              dmp_find_test_cases['dstcoordestimate'])

    assert result == dmp_find_test_cases['expected_result']


@pytest.fixture(params=[{'srcblcoord': 0,
                          'expected_result': 0},
                        {'srcblcoord': 2,
                          'expected_result': 4},
                        {'srcblcoord': 7,
                          'expected_result': 7}])
def get_updated_coord_test_cases(request):
    return request.param

def test_updated_coord(inputs, get_updated_coord_test_cases):
    updater = Blupdate(inputs['srcbl'], inputs['dstbl'], context_len=4)

    result = updater.get_updated_coord(get_updated_coord_test_cases['srcblcoord'])

    assert result == get_updated_coord_test_cases['expected_result']


# Test on real text
data_path = Path('tests/data/blupdate')

@pytest.fixture(scope='module')
def updater():
    srcbl = (data_path/'v1'/'v1.opf'/'base.txt').read_text()
    dstbl = (data_path/'v2'/'v2.opf'/'base.txt').read_text()
    updater = Blupdate(srcbl, dstbl)
    return updater

def get_layer(layer):
    src_layer = data_path/'v1'/'v1.opf'/'layers'/f'{layer}.yml'
    dst_layer = data_path/'v2'/'v2.opf'/'layers'/f'{layer}.yml'
    return yaml.safe_load(src_layer.open()), yaml.safe_load(dst_layer.open())


@pytest.fixture(params=[{'layer': 'title'},
                        {'layer': 'yigchung'},
                        {'layer': 'quotes'},
                        {'layer': 'tsawa'},
                        {'layer': 'sapche'}])
def layers_test_cases(request):
    return request.param

def test_get_updated_coord_all(updater, layers_test_cases):
    src_ann_cc, dst_ann_cc = get_layer(layers_test_cases['layer'])
    if layers_test_cases['layer'] == 'title':
        result = updater.get_updated_coord(src_ann_cc[0])
        assert result == dst_ann_cc[0]
    else:
        start_result = updater.get_updated_coord(src_ann_cc[0][0])
        end_result = updater.get_updated_coord(src_ann_cc[0][1])
        assert start_result == dst_ann_cc[0][0]
        assert end_result == dst_ann_cc[0][1] 