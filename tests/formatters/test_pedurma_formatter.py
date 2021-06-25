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
            ('', {'page_index': '42a', 'page_info': None, 'reference': None, 'span': {'start': 1, 'end': 120}}), 
            ('', {'page_index': '42b', 'page_info': None, 'reference': None, 'span': {'start': 122, 'end': 361}} ), 
            ('', {'page_index': '43a', 'page_info': None, 'reference': None, 'span': {'start': 363, 'end': 538}})
            ]],
        AnnType.pedurma_note:[[
            ('', {'span': {'start': 14, 'end': 18}, 'variants': {'«པེ་»': 'མཚན་བྱང་འདི་ལྟར་བཀོད།', '«སྣར་»': '', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»མཚན་བྱང་འདི་ལྟར་བཀོད།>'} ),
            ('', {'span': {'start': 33, 'end': 40}, 'variants': {'«པེ་»': 'ཏྲ་ན་', '«སྣར་»': 'ཏྲ་ན་', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»ཏྲ་ན་>'}),
            ('', {'span': {'start': 57, 'end': 61}, 'variants': {'«པེ་»': 'ཀྱི་', '«སྣར་»': 'ཀྱི་', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»ཀྱི་>'}),
            ('', {'span': {'start': 127, 'end': 130}, 'variants': {'«པེ་»': 'ཅེས་', '«སྣར་»': 'ཅེས་', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»ཅེས་>'}),
            ('', {'span': {'start': 136, 'end': 140}, 'variants': {'«པེ་»': 'ཀྱི་', '«སྣར་»': 'ཀྱི་', '«སྡེ»': '', '«ཅོ་»': 'གི་'}, 'collation_note':'<«ཅོ་»གི་«པེ་»«སྣར་»ཀྱི་>'}),
            ('', {'span': {'start': 204, 'end': 207}, 'variants': {'«པེ་»': 'ཟད་', '«སྣར་»': 'ཟད་', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»ཟད་>'}),
            ('', {'span': {'start': 226, 'end': 233}, 'variants': {'«པེ་»': 'སྲེག', '«སྣར་»': 'སྲེག', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»སྲེག>'}),
            ('', {'span': {'start': 321, 'end': 324}, 'variants': {'«པེ་»': '', '«སྣར་»': 'འཆི་', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«སྣར་»འཆི་>'}),
            ('', {'span': {'start': 363, 'end': 365}, 'variants': {'«པེ་»': 'གཅིག', '«སྣར་»': 'གཅིག', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»གཅིག>'}),
            ('', {'span': {'start': 418, 'end': 428}, 'variants': {'«པེ་»': 'བྲམ་ཟེ་', '«སྣར་»': 'བྲམ་ཟེ་', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»«སྣར་»བྲམ་ཟེ་>'}),
            ('', {'span': {'start': 496, 'end': 504}, 'variants': {'«པེ་»': 'ཛ་ར་དན་', '«སྣར་»': '', '«སྡེ»': '', '«ཅོ་»': ''}, 'collation_note':'<«པེ་»ཛ་ར་དན་>'})
            ]]
    }
    assert expected_layers == layers


def test_get_base():
    expected_base = Path('./tests/data/formatter/pedurma/expected_base.txt').read_text(encoding='utf-8')
    preview_text = Path('./tests/data/formatter/pedurma/preview_text.txt').read_text(encoding='utf-8')
    formatter = PedurmaFormatter()
    base_text = formatter.base_extract(preview_text)
    assert expected_base == base_text