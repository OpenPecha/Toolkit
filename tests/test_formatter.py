import json
from pathlib import Path

import pytest

from openpecha.formatters import GoogleOCRFormatter, HFMLFormatter, TsadraFormatter
from openpecha.formatters.hfml import LocalIdManager


class TestHFMLFormatter:
    def test_tofu_id(self):
        formatter = HFMLFormatter()
        formatter.dirs = {}
        formatter.dirs["layers_path"] = Path("tests/data/formatter/hfml/tofu-id")
        layers = [layer.stem for layer in formatter.dirs["layers_path"].iterdir()]
        old_layers = formatter.get_old_layers(layers)
        local_id2uuid = LocalIdManager(old_layers)
        local_id2uuid.add("tsawa", 1231232)
        d = local_id2uuid.serialize("tsawa")
        print(d)


class TestGoogleOCRFormatter:
    @pytest.fixture(scope="class")
    def get_resources(self):
        data_path = Path("tests/data/formatter/google_ocr/W0001/v001")
        responses = [
            (json.load(fn.open()), fn.stem)
            for fn in sorted(list((data_path).iterdir()))
        ]
        formatter = GoogleOCRFormatter()
        return formatter, data_path, responses

    def test_get_base_text(self, get_resources):
        formatter, data_path, responses = get_resources
        formatter.build_layers(responses, "")

        result = formatter.get_base_text()
        print(result)

        # TODO: create base-text
        # expected = (data_path/'v001.txt').read_text()
        # assert result == expected

    def test_build_layers(self, get_resources):
        formatter, data_path, responses = get_resources

        result = formatter.build_layers(responses, "")

        expected = {"pages": [(0, 19), (24, 888), (893, 1607), (1612, 1809)]}

        for result_page, expected_page in zip(result["pages"], expected["pages"]):
            assert result_page[:2] == expected_page


class TestTsadraFormatter:
    def test_tsadra_formatter(self):
        m_text_01 = Path("tests/data/formatter/tsadra/htmls/cover.xhtml").read_text()
        m_text_02 = Path(
            "tests/data/formatter/tsadra/htmls/tsadra_02.xhtml"
        ).read_text()
        m_texts = [m_text_01, m_text_02]
        formatter = TsadraFormatter()
        for m_text in m_texts:
            text = formatter.text_preprocess(m_text)
            formatter.build_layers(text)
        result = formatter.get_result()

        expected_result = {
            "book_title": [(0, 84)],
            "author": [(86, 109), (111, 134), (136, 181)],
            "chapter_title": [(183, 200)],
            "tsawa": [(4150, 4300), (5122, 5298)],
            "quotation": [(3993, 4131), (4302, 4417)],
            "sabche": [(5091, 5120), (7313, 7375)],
            "yigchung": [(7273, 7311)],
        }

        for layer in result:
            print(result[layer])
            assert result[layer] == expected_result[layer]

    def test_tsadra_get_base_text(self):
        m_text1 = Path("tests/data/formatter/tsadra/htmls/cover.xhtml").read_text()
        m_text2 = Path("tests/data/formatter/tsadra/htmls/tsadra_02.xhtml").read_text()
        texts = [m_text1, m_text2]
        formatter = TsadraFormatter()
        for text in texts:
            text = formatter.text_preprocess(text)
            formatter.build_layers(text)
        result = formatter.get_base_text()
        expected1 = Path("tests/data/formatter/tsadra/tsadra_base1.txt").read_text()
        assert result == expected1


if __name__ == "__main__":
    TestHFMLFormatter().test_tofu_id()
