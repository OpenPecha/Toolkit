from openpecha.proofreading import get_vol_info

def test_get_vol_info():
    expected_vol_info = [
        '330debd2cd0440079408cbf3a7903ed8',
        '6796e040db684bc09365121dd248acd1',
        'f831c8c16c9b46bd80ff92840891bb8a',
        'b7a462a774b54643a6334ed2fcfb7342',
        '35580e1fe51b430492cd575d712eef60',
        '209c5ffa1f454aad83469bdcc06816ab',
        '9d2126031717494e95bf58d63da85a7a',
        'a3e8e674294a4eed8aee7ddb3588952e',
    ]
    pecha_id = "P0003"
    pecha_path = "./tests/data/proofreading/P0003/"
    vol_num = 1
    vol_info = get_vol_info(pecha_id, vol_num, pecha_path=pecha_path)
    assert expected_vol_info == vol_info