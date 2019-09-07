import pytest

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
                         'expected_result': ('abe', 'ghi')},
                         {'srcblcoord': 7, 
                         'expected_result': ('ghi', 'kl')}])
def get_context_test_cases(request):
    return request.param

def test_get_context(inputs, get_context_test_cases):
    updater = Blupdate(inputs['srcbl'], inputs['dstbl'], context_len=3)

    result = updater.get_context(get_context_test_cases['srcblcoord'])

    assert result == get_context_test_cases['expected_result']