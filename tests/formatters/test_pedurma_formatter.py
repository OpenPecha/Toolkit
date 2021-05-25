from pathlib import Path
from openpecha.formatters import PedurmaFormatter
from openpecha.formatters.layers import AnnType


def test_pedurma_formatter():
    preview_text = Path('./tests/data/formatter/pedurma/preview_text.txt').read_text(encoding='utf-8')
    formatter = PedurmaFormatter()
    formatter.build_layers(preview_text)
    layers = formatter.get_result()
    expected_layers = {
        AnnType.topic: [],
        AnnType.sub_topic: [],
        AnnType.pagination: [[
            ('', {'page_num': '113', 'span': {'vol': '1', 'start': 0, 'end': 119}}), 
            ('', {'page_num': '114', 'span': {'vol': '1', 'start': 120, 'end': 360}} ), 
            ('', {'page_num': '115', 'span': {'vol': '1', 'start': 361, 'end': 538}})
            ]],
        AnnType.pedurma_note:[[
            ('', {'span': {'start': 13, 'end': 17}, 'note': {'pe': 'མཚན་བྱང་འདི་ལྟར་བཀོད།', 'nar': '', 'der': '', 'co': ''}} ),
            ('', {'span': {'start': 32, 'end': 39}, 'note': {'pe': 'ཏྲ་ན་', 'nar': 'ཏྲ་ན་', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 56, 'end': 60}, 'note': {'pe': 'ཀྱི་', 'nar': 'ཀྱི་', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 126, 'end': 129}, 'note': {'pe': 'ཅེས་', 'nar': 'ཅེས་', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 135, 'end': 139}, 'note': {'pe': 'ཀྱི་', 'nar': 'ཀྱི་', 'der': '', 'co': 'གི་'}}),
            ('', {'span': {'start': 203, 'end': 206}, 'note': {'pe': 'ཟད་', 'nar': 'ཟད་', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 225, 'end': 232}, 'note': {'pe': 'སྲེག', 'nar': 'སྲེག', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 320, 'end': 323}, 'note': {'pe': '', 'nar': 'འཆི་', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 362, 'end': 364}, 'note': {'pe': 'གཅིག', 'nar': 'གཅིག', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 417, 'end': 427}, 'note': {'pe': 'བྲམ་ཟེ་', 'nar': 'བྲམ་ཟེ་', 'der': '', 'co': ''}}),
            ('', {'span': {'start': 495, 'end': 503}, 'note': {'pe': 'ཛ་ར་དན་', 'nar': '', 'der': '', 'co': ''}})
            ]]
    }
    assert expected_layers == layers


def test_get_base():
    expected_base = Path('./tests/data/formatter/pedurma/expected_base.txt').read_text(encoding='utf-8')
    preview_text = Path('./tests/data/formatter/pedurma/preview_text.txt').read_text(encoding='utf-8')
    formatter = PedurmaFormatter()
    base_text = formatter.base_extract(preview_text)
    assert expected_base == base_text