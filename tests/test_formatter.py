import json
from pathlib import Path

import pytest

from openpecha.formatters import TsadraFormatter
from openpecha.formatters import HFMLFormatter
from openpecha.formatters import GoogleOCRFormatter



class TestHFMLFormatter:

    def test_get_base_text(self):
        m_text = Path('tests/data/formatter/hfml/kangyur_01.txt').read_text()
        formatter = HFMLFormatter()

        text = formatter.text_preprocess(m_text)
        formatter.build_layers(text, len([text]))
        result = formatter.get_base_text()

        expected = Path('tests/data/formatter/hfml/kangyur_base.txt').read_text()

        assert result == expected


    def test_build_layers(self):
        m_text1 = Path('tests/data/formatter/hfml/kangyur_01.txt').read_text()
        m_text2 = Path('tests/data/formatter/hfml/kangyur_02.txt').read_text()
        m_text3 = Path('tests/data/formatter/hfml/kangyur_03.txt').read_text()
        formatter = HFMLFormatter()

        text1 = formatter.text_preprocess(m_text1)
        text2 = formatter.text_preprocess(m_text2)
        text3 = formatter.text_preprocess(m_text3)
        texts = [text1, text2, text3]
        for text in texts:
            result = formatter.build_layers(text, len(texts))

        result = formatter.get_result()
        
        expected_result = {
            'page': [[(0, 24, 'kk', '1a'), (27, 676, 'kl', '1b'), (679, 2173, 'lm', '2a')], [(0, 0, 'kk', '1a'),(0,266,'','1b')], [(0, 266, 'ko', '1a')]],
            'topic': [[(0, 2173, 1,'T1')],[(0, 266, 2,'T2'),(0,26,3,'T2')], [(26, 266, 3,'T3')]],
            'sub_topic': [[(0, 1352, 1,'T1-1'), (1353, 1496, 1,'T1-2'), (1497, 2173, 1,'T1-6')], [(0, 140, 2,'T1-8'),(141,266,2,'T1-9'),(0,26,3,'T1-9')],[(27,266,3,'T3-1')]],
            'error': [[(1838, 1843, 'མཆིའོ་')], [], []],
            'absolute_error': [[(2040, 2042), (2044, 2045)], [], []],
            'note':[[1518, 1624, 1938], [], []]
        }

        for layer in result:
            assert result[layer] == expected_result[layer]


class TestGoogleOCRFormatter:

    @pytest.fixture(scope='class')
    def get_resources(self):
        data_path = Path('tests/data/formatter/google_ocr/W0001/v001')
        responses = [json.load(fn.open()) for fn in sorted(list((data_path/'resources').iterdir()))]
        formatter = GoogleOCRFormatter()
        return formatter, data_path, responses

    
    def test_get_base_text(self, get_resources):
        formatter, data_path, responses = get_resources
        formatter.build_layers(responses)
        
        result = formatter.get_base_text()

        expected = (data_path/'v001.txt').read_text()
        assert result == expected

    
    def test_build_layers(self, get_resources):
        formatter, data_path, responses = get_resources

        result = formatter.build_layers(responses)

        expected = {
            'page': [(0, 19), (24, 888), (893, 1607), (1612, 1809)],
        }

        for result_page, expected_page in zip(result['page'], expected['page']):
            assert result_page[:2] == expected_page