import pytest

from openpoti.blupdate import Blupdate


@pytest.fixture(params=[{'srcbl': 'abefghijkl',
                         'dstbl': 'abcdefgkl',
                         'expected_result': [(0,2,0), (2,5,2), (8,10,-1)]}])
def test_cases(request):
    return request.param

def test_compute_cctv(test_cases):
    updater = Blupdate(test_cases['srcbl'], test_cases['dstbl'])

    result = updater.cctv

    assert result == test_cases['expected_result']