import pytest

from openpoti.blupdate import Blupdate


@pytest.fixture(scope='module')
def preconfigured_blupdate():
    srcbl = 'abefghijkl'
    dstbl = 'abcdefgkl'
    
    updater = Blupdate(srcbl, dstbl)

    return updater


def test_compute_cctv(preconfigured_blupdate):
    result = preconfigured_blupdate.cctv

    expected_result = [(0,2,0), (2,5,2), (8,10,-1)]

    assert result == expected_result