import json
from pathlib import Path

import pytest

from openpecha.formatters import TsadraFormatter
from openpecha.formatters import GoogleOCRFormatter



# def test_build_layers():
#     m_text = Path('tests/data/formatter/tsadra_01.txt').read_text()
#     formatter = TsadraFormatter()

#     text = formatter.text_preprocess(m_text)
#     result = formatter.build_layers(text)

#     expected_result = {
#         'title': [0, 17],
#         'yigchung': [193, 830],
#         'tsawa': [919, 1073],
#         'quotes': [1733, 1777],
#         'sapche': [1318, 1393]
#     }

#     for layer, ann in expected_result.items():
#         assert result[layer][0] == expected_result[layer]



class TestGoogleOCRFormatter:

    @pytest.fixture(scope='class')
    def get_resources(self):
        opf_path = Path('tests/data/google_ocr/01.opf')
        responses = [json.load(fn.open()) for fn in sorted(list((opf_path/'resources/v001').iterdir()))]
        formatter = GoogleOCRFormatter()
        return formatter, opf_path, responses

    def test_get_base_text(self, get_resources):
        formatter, opf_path, responses = get_resources

        result = formatter.get_base_text(responses)
        # (opf_path/'bases'/'test.txt').write_text(result)

        expected = (opf_path/'bases/v001.txt').read_text()
        assert result == expected