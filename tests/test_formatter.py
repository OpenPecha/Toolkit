import json
from pathlib import Path

import pytest

from openpecha.formatters import TsadraFormatter
from openpecha.formatters import GoogleOCRFormatter



def test_build_layers():
    m_text = Path('tests/data/formatter/tsadra_01.txt').read_text()
    formatter = TsadraFormatter()

    text = formatter.text_preprocess(m_text)
    result = formatter.build_layers(text)

    expected_result = {
        'title': [0, 17],
        'yigchung': [193, 830],
        'tsawa': [919, 1073],
        'quotes': [1733, 1777],
        'sapche': [1318, 1393]
    }

    for layer, ann in expected_result.items():
        assert result[layer][0] == expected_result[layer]



class TestGoogleOCRFormatter:

    @pytest.fixture(scope='class')
    def get_resources(self):
        opf_path = Path('tests/data/google_ocr/01.opf')
        responses = [json.load(fn.open()) for fn in sorted(list((opf_path/'resources/v001').iterdir()))]
        formatter = GoogleOCRFormatter()
        return formatter, opf_path, responses

    
    def test_get_base_text(self, get_resources):
        formatter, opf_path, responses = get_resources
        formatter.build_layers(responses)
        
        result = formatter.get_base_text(responses)

        expected = (opf_path/'bases/v001.txt').read_text()
        assert result == expected

    
    def test_build_layers(self, get_resources):
        formatter, opf_path, responses = get_resources

        result = formatter.build_layers(responses)

        expected = {
            'page': [(0, 19), (24, 888), (893, 1607), (1612, 1809)],
            'line': [
                [(0, 19)],
                [
                    (24, 41), (43, 46), (48, 94), (96, 151), (153, 208), (210, 263),
                    (265, 318), (320, 369), (371, 428), (430, 485), (487, 542), (544, 594),
                    (596, 653), (655, 714), (716, 772), (774, 830), (832, 888)
                ]
            ]
        }

        for result_page, expected_page in zip(result['page'], expected['page']):
            assert result_page[:2] == expected_page
        
        assert result['line'][:2] == expected['line']