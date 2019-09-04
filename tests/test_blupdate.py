import pytest

from openpoti.blupdate import Blupdate



@pytest.mark.parametrize('srcbl, dstbl, expected_result',
                         [
                             ('abefghijkl', 'abcdefgkl', [(0,2,0), (2,5,2), (8,10,-1)])
                         ])
def test_compute_cctv(srcbl, dstbl, expected_result):
    updater = Blupdate(srcbl, dstbl)

    result = updater.cctv

    assert result == expected_result