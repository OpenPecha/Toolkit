from openpecha.proofreading import get_vol_info

def test_get_vol_info():
    expected_vol_info = [
        {
        'id': 'c4c64b7e3a714a4ab3db3375a7c22196',
        'image_group_id': 'I0919',
        'title': '',
    },
    ]
    pecha_id = "P0003"
    pecha_path = "./tests/data/proofreading/P0003/"
    vol_info = get_vol_info(pecha_id, pecha_path=pecha_path)
    assert expected_vol_info == vol_info