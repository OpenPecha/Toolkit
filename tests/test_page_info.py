from openpecha.proofreading import get_pages_info, get_page
from pathlib import Path


def test_get_pages_info():
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
    vol_id = 'c4c64b7e3a714a4ab3db3375a7c22196'
    vol_info = get_pages_info(pecha_id, vol_id, pecha_path=pecha_path)
    assert expected_vol_info == vol_info


def test_get_page():
    pecha_id = "P0003"
    vol_id = 'c4c64b7e3a714a4ab3db3375a7c22196'
    page_id = "6796e040db684bc09365121dd248acd1"
    pecha_path = './tests/data/proofreading/P0003/'
    page_info = get_page(pecha_id, vol_id, page_id, pecha_path)
    expected_page_info = {
        'content': """༄༅༅། །རྒྱ་གར་སྐད་དུ། ཨཱརྱ་པྲཛྙཱ་པཱ་ར་མི་ཏཱ་སཉྩ་ཡ་གཱ་ཐཱ། བོད་སྐད་དུ། འཕགས་པ་ཤེས་རབ་ཀྱི་ཕ་རོལ་ཏུ་ཕྱིན་པ་སྡུད་པ་ཚིགས་སུ་བཅད་པ། འཕགས་པ་
འཇམ་དཔལ་ལ་ཕྱག་འཚལ་ལོ། །དེ་ནས་ཡང་བཅོམ་ལྡན་འདས་ཀྱིས་འཁོར་བཞི་པོ་དེ་དག་ཡང་དག་པར་རབ་ཏུ་དགའ་བར་མཛད་པའི་ཕྱིར་ཡང་ཤེས་རབ་ཀྱི་ཕ་རོལ་ཏུ་ཕྱིན་པ་འདི་སྟོན་
ཅིང་། དེའི་ཚེ་ཚིགས་སུ་བཅད་པ་འདི་དག་བཀའ་སྩལ་ཏོ། །དགའ་དང་གུས་དང་དད་པའི་མཆོག་ནི་ཉེར་བཞག་སྟེ། །སྒྲིབ་པ་ཉོན་མོངས་བསལ་ནས་དྲི་མ་ལས་འདས་པ། །འགྲོ་དོན་
མངོན་ཞུགས་དེས་པའི་ཤེས་རབ་ཕ་རོལ་ཕྱིན། །གང་ལ་དཔའ་རྣམས་སྤྱོད་པ་དེ་ནི་མཉན་པར་གྱིས། །སྐབས་དང་པོ་རྣམ་པ་ཐམས་ཅད་མཁྱེན་པ་ཉིད་བསྟན། འཛམ་བུའི་གླིང་འདིར་ཆུ་ཀླུང་ཇི་
སྙེད་ཅིག་འབབ་ཅིང་། །མེ་ཏོག་འབྲས་ལྡན་སྨན་དང་ནགས་ཚལ་སྐྱེད་བྱེད་པ། །མ་དྲོས་གནས་པའི་ཀླུ་དབང་ཀླུ་བདག་བརྟེན་གནས་ཏེ། །དེ་ནི་ཀླུ་ཡི་བདག་པོ་དེ་ཡི་མཐུ་དཔལ་ཡིན། །""",
        'image_url': 'https://iiif.bdrc.io/bdr:I0919::09190004.tif/full/max/0/default.jpg'
    }
    assert expected_page_info == page_info
