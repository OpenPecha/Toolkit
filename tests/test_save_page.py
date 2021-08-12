import copy
import os
import yaml
from pathlib import Path
from openpecha.blupdate import *
from openpecha.proofreading import update_index, get_old_layers, save_page, get_page

def to_yaml(dict_):
    return yaml.dump(dict_, sort_keys=False, allow_unicode=True, Dumper=yaml.CDumper)

def test_update_index():
    vol_offset = 2
    vol_num = 1
    page_start = 300
    vol_meta = {
        'image_group_id': 'I0919',
        'title': '',
        'base_file': 'v001.txt'
    }
    old_pecha_idx = load_yaml(Path('./tests/data/proofreading/old_index.yml'))
    new_pecha_idx = update_index(vol_offset, vol_meta, page_start, old_pecha_idx)
    new_pecha_idx = to_yaml(new_pecha_idx)
    expected_idx = Path('./tests/data/proofreading/expected_index.yml').read_text(encoding='utf-8')
    assert new_pecha_idx == expected_idx


def test_update_layers():
    pecha_opf_path = Path('./tests/data/proofreading/P0003')
    pecha_id = "P0003"
    vol_id = 'v001'
    old_vol = (pecha_opf_path / f'P0003.opf/base/v001.txt').read_text(encoding='utf-8')
    new_vol = Path('./tests/data/proofreading/new_vol.txt').read_text(encoding='utf-8')
    updater = Blupdate(old_vol, new_vol)
    old_layers = get_old_layers(pecha_opf_path, pecha_id, vol_id)
    for layer_name, old_layer in old_layers.items():
        update_ann_layer(old_layer, updater)
        expected_layer = load_yaml(Path(f'./tests/data/proofreading/expected_layers/{layer_name}.yml'))
        assert old_layer == expected_layer


def test_integration():
    os.system('cp -r ./tests/data/proofreading/P0003 ./tests/data/proofreading/P0003_copy')
    pecha_opf_path = './tests/data/proofreading/P0003_copy/'
    pecha_id = "P0003"
    vol_id = 'c4c64b7e3a714a4ab3db3375a7c22196'
    page_id = '9d2126031717494e95bf58d63da85a7a'
    new_page_content = """སློབ། །གང་ཞིག་སློབ་མི་སློབ་ལ་མི་སློབ་དེ་སློབ་ཡིན། །གཟུགས་འཕེལ་ཡོངས་སུ་ཉམས་དང་ཡོངས་སུ་གཟུང་ཕྱིར་མིན། །ཆོས་རྣམས་སྣ་ཚོགས་ཡོངས་སུ་གཟུང་ཕྱིར་མི་སློབ་པར། །སློབ་ཅིང་ཐམས་ཅད་མཁྱེན་པ་ཉིད་ཀྱང་ཡོངས་འཛིན་ལ། །ངེས་འབྱུང་
གང་ཡིན་འདི་ནི་ཡོན་ཏན་དགའ་བའི་སློབ། །གཟུགས་ནི་ཤེས་རབ་མ་ཡིན་གཟུགས་ལ་ཤེས་རབ་མེད། །རྣམ་ཤེས་འདུ་ཤེས་ཚོར་དང་སེམས་པ་འདི་དག་ནི། །ཤེས་རབ་མ་ཡིན་འདི་དག་ལ་ཡང་ཤེས་རབ་མེད། །འདི་ནི་ནམ་མཁའི་ཁམས་དང་མཚུངས་ཏེ་ཐ་དད་མེད། །དམིགས་
པ་རྣམས་ཀྱི་རང་བཞིན་དེ་ནི་ཕ་མཐའ་མེད། །སེམས་ཅན་རང་བཞིན་གང་ཡིན་དེ་ཡང་ཕ་མཐའ་མེད། །ནམ་མཁའི་ཁམས་ཀྱི་རང་བཞིན་དེ་ཡང་ཕ་མཐའ་མེད། །འཇིག་རྟེན་མཁྱེན་པའི་ཤེས་རབ་དེ་ཡང་ཕ་མཐའ་མེད། །འདུ་ཤེས་ཚུ་རོལ་ཡིན་ཞེས་འདྲེན་པས་ཡོངས་སུ་བསྒྲགས། །
འདུ་ཤེས་རྣམ་པར་བཤིག་ནས་སྤོང་བ་ཕ་རོལ་འགྲོ། །གང་དག་འདུ་ཤེས་བྲལ་བ་འདི་ནི་རྗེས་ཐོབ་པ། །དེ་དག་ཕ་རོལ་ཕྱིན་ནས་སྟོན་པའི་བཀའ་ལ་གནས། hello།གལ་ཏེ་སྟོན་པས་ཀྱང་ནི་གང་གཱའི་བྱེ་སྙེད་ཀྱི། །བསྐལ་པར་བཞུགས་ཏེ་སེམས་ཅན་ཞེས་སྒྲ་ཡོངས་བསྒྲགས་ཀྱང་། །གཟོད་
ནས་དག་པས་སེམས་ཅན་སྐྱེ་བར་ག་ལ་འགྱུར། །འདི་ནི་ཤེས་རབ་ཕ་རོལ་ཕྱིན་མཆོག་སྤྱོད་པ་ཡིན། །གང་ཚེ་ང་ནི་ཕ་རོལ་ཕྱིན་པ་མཆོག་འདི་དང་། །འཐུན་པར་སྨྲ་གྱུར་དེ་ཚེ་སྔོན་གྱི་སྐྱེས་མཆོག་གིས། །མ་འོངས་པ་ཡི་དུས་ན་སངས་རྒྱས་འགྱུར་རོ་ཞེས། །ང་ལུང་བསྟན་པར་གྱུར་ཅེས་རྒྱལ་
བ་དེ་སྐད་གསུང་། །ཤེས་རབ་ཕ་རོལ་ཕྱིན་པ་གང་ལ་མགོན་སྤྱོད་པ། །འདི་ནི་གང་ཞིག་གུས་བྱས་འཛིན་དང་ཆུབ་བྱེད་པ། །དེ་ལ་དུག་དང་མཚོན་དང་མེ་དང་ཆུས་མི་ཚུགས། །བདུད་དང་བདུད་ཀྱི་ཕྱོགས་ཀྱིས་གླགས་ཀྱང་རྙེད་མི་འགྱུར། །ལ་ལས་བདེ་གཤེགས་ཡོངས་སུ་
མྱ་ངན་འདས་པ་ཡི། །མཆོད་རྟེན་རིན་ཆེན་བདུན་ལས་བྱས་ཤིང་མཆོད་བྱེད་ལ། །བདེ་བར་གཤེགས་པའི་མཆོད་རྟེན་དེ་དག་གང་གཱ་ཡི། །བྱེ་མ་སྙེད་ཀྱིས་བྱེ་བ་ཕྲག་སྟོང་ཞིང་བཀང་སྟེ། །ཡོངས་སུ་བརྟག་བཟུང་ཞིང་རྣམས་བྱེ་བ་མཐའ་ཡས་ན། །སེམས་ཅན་ཇི་སྙེད་"""
    save_page(pecha_id, vol_id, page_id, new_page_content, pecha_path=pecha_opf_path)
    new_page_info = get_page(pecha_id, vol_id, page_id, pecha_path=pecha_opf_path)
    assert new_page_info['content'] == new_page_content
    os.system('rm -r ./tests/data/proofreading/P0003_copy')