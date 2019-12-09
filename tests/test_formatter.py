import json
from pathlib import Path

import pytest

from openpecha.formatters import TsadraFormatter
from openpecha.formatters import kangyurFormatter
from openpecha.formatters import GoogleOCRFormatter



class TestkangyurFormatter:

    def test_kangyur_formatter(self):
        m_text = Path('tests/data/formatter/kangyur_01.txt').read_text()
        formatter = kangyurFormatter()

        text = formatter.text_preprocess(m_text)
        result = formatter.build_layers(text)

        expected_result = {
            'page': [(0, 24), (27, 676), (679, 2173)],
            'topic': [(27, 2173)],
            'sub_topic': [[(27, 1351), (1352, 1494), (1495, 2173)]],
            'error': [(1838,1843,'མཆིའོ་')],
            'yigchung': [(2040,2042),(2044,2045)],
            'absolute_error':[1518,1624,1938]
        }

        for layer in result:
            print(result[layer])
            assert result[layer] == expected_result[layer]


    def test_kangyur_get_base_text(self):
        m_text = Path('tests/data/formatter/kangyur_01.txt').read_text()
        formatter = kangyurFormatter()

        text = formatter.text_preprocess(m_text)
        formatter.build_layers(text)
        result = formatter.get_base_text()

        expected = Path('tests/data/formatter/kangyur_base.txt').read_text()

        assert result == expected


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

class TestTsadraFormatter:

    def test_tsadra_formatter(self):
        m_text_01 = Path('tests/data/formatter/tsadra/tsadra_01.xhtml').read_text()
        m_text_02 = Path('tests/data/formatter/tsadra/tsadra_02.xhtml').read_text()
        m_texts = [m_text_01, m_text_02]
        formatter = TsadraFormatter()
        for m_text in m_texts:
            text = formatter.text_preprocess(m_text)
            formatter.build_layers(text)
        result = formatter.get_result()
       
        expected_result = {
            'book_title':[(0,85)],
            'author':[(86,110),(111,135),(136,182)],
            'chapter_title':[(183,201)],
            'tsawa':[(4150,4301),(5122,5299)],
            'quotes':[(3993,4132),(4302,4418)],
            'sabche':[(5091,5121),(7313,7376)],
            'yigchung':[(7273,7312)]
        }

        for layer in result:
            print(result[layer])
            assert result[layer] == expected_result[layer]


    def test_tsadra_get_base_text(self):
        m_text1 = Path('tests/data/formatter/tsadra/tsadra_01.xhtml').read_text()
        m_text2 = Path('tests/data/formatter/tsadra/tsadra_02.xhtml').read_text()
        texts = [m_text1, m_text2]
        result = []
        formatter = TsadraFormatter()
        for text in texts:
            text = formatter.text_preprocess(text)
            formatter.build_layers(text)
            result.append(formatter.get_base_text())

        expected1 = Path('tests/data/formatter/tsadra/tsadra_base1.txt').read_text()
        expected2 = Path('tests/data/formatter/tsadra/tsadra_base2.txt').read_text()
        expecteds = [expected1, expected2]
        for i in range(0,2):
            assert result[i] == expecteds[i]