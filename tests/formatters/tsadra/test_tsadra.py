from pathlib import Path

from openpecha.formatters import TsadraFormatter
from openpecha.formatters.layers import AnnType


class TestTsadraFormatter:
    def test_tsadra_formatter(self):
        m_text_01 = (
            Path(__file__).parent / "data" / "htmls" / "cover.xhtml"
        ).read_text()
        m_text_02 = (
            Path(__file__).parent / "data" / "htmls" / "tsadra_02.xhtml"
        ).read_text()
        m_texts = [m_text_01, m_text_02]
        formatter = TsadraFormatter()
        for m_text in m_texts:
            text = formatter.text_preprocess(m_text)
            formatter.build_layers(text)
        result = formatter.get_result()

        expected_result = {
            AnnType.book_title: [[(None, {"span": {"start": 0, "end": 84}})]],
            AnnType.sub_title: [[]],
            AnnType.book_number: [[]],
            AnnType.poti_title: [[]],
            AnnType.author: [
                [
                    (None, {"span": {"start": 86, "end": 109}}),
                    (None, {"span": {"start": 111, "end": 134}}),
                    (None, {"span": {"start": 136, "end": 181}}),
                ]
            ],
            AnnType.chapter: [[(None, {"span": {"start": 183, "end": 200}})]],
            AnnType.topic: [[]],
            AnnType.sub_topic: [[]],
            AnnType.pagination: [[]],
            AnnType.tsawa: [
                [
                    (None, {"span": {"start": 4150, "end": 4300}, "isverse": True}),
                    (None, {"span": {"start": 5122, "end": 5298}, "isverse": True}),
                ]
            ],
            AnnType.citation: [
                [
                    (None, {"span": {"start": 3993, "end": 4132}, "isverse": False}),
                    (None, {"span": {"start": 4302, "end": 4418}, "isverse": True}),
                ]
            ],
            AnnType.sabche: [
                [
                    (None, {"span": {"start": 5091, "end": 5120}}),
                    (None, {"span": {"start": 7313, "end": 7375}}),
                ]
            ],
            AnnType.yigchung: [[(None, {"span": {"start": 7273, "end": 7311}})]],
            AnnType.footnote: [[]],
        }

        for layer in result:
            assert result[layer] == expected_result[layer]

    def test_tsadra_get_base_text(self):
        m_text1 = (Path(__file__).parent / "data" / "htmls" / "cover.xhtml").read_text()
        m_text2 = (
            Path(__file__).parent / "data" / "htmls" / "tsadra_02.xhtml"
        ).read_text()
        texts = [m_text1, m_text2]
        formatter = TsadraFormatter()
        for text in texts:
            text = formatter.text_preprocess(text)
            formatter.build_layers(text)
        result = formatter.get_base_text()
        expected1 = (Path(__file__).parent / "data" / "tsadra_base1.txt").read_text()
        assert result == expected1
