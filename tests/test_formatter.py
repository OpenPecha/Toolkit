import json
from pathlib import Path

import pytest

from openpecha.formatters import GoogleOCRFormatter, HFMLFormatter, TsadraFormatter
from openpecha.formatters.formatter import LocalIdManager
from openpecha.formatters.layers import AnnType


class TestHFMLFormatter:
    def test_get_base_text(self):
        m_text = Path("tests/data/formatter/hfml/kangyur_01.txt").read_text()
        formatter = HFMLFormatter()

        text = formatter.text_preprocess(m_text)
        formatter.build_layers(text, len([text]))
        result = formatter.get_base_text()

        expected = Path("tests/data/formatter/hfml/kangyur_base.txt").read_text()

        assert result == expected

    def test_build_layers(self):
        m_text1 = Path("tests/data/formatter/hfml/kangyur_01.txt").read_text()
        m_text2 = Path("tests/data/formatter/hfml/kangyur_02.txt").read_text()
        m_text3 = Path("tests/data/formatter/hfml/kangyur_03.txt").read_text()
        formatter = HFMLFormatter()

        text1 = formatter.text_preprocess(m_text1)
        text2 = formatter.text_preprocess(m_text2)
        text3 = formatter.text_preprocess(m_text3)
        texts = [text1, text2, text3]
        for text in texts:
            result = formatter.build_layers(text, len(texts))

        result = formatter.get_result()
        expected_result = {
            AnnType.book_title: [[], [], []],
            AnnType.book_number: [[], [], []],
            AnnType.author: [[], [], []],
            AnnType.poti_title: [
                [(None, {"span": {"start": 0, "end": 24}})],
                [(None, {"span": {"start": 0, "end": 24}})],
                [(None, {"span": {"start": 0, "end": 24}})],
            ],
            AnnType.chapter: [[(None, {"span": {"start": 98, "end": 125}})], [], []],
            AnnType.citation: [
                [],
                [
                    (1000020, {"span": {"start": 164, "end": 202}}),
                    (1000021, {"span": {"start": 204, "end": 241}}),
                ],
                [(1000024, {"span": {"start": 97, "end": 162}})],
            ],
            AnnType.pagination: [
                [
                    (
                        1000000,
                        {
                            "page_index": "1a",
                            "page_info": "kk",
                            "reference": None,
                            "span": {"start": 0, "end": 24},
                        },
                    ),
                    (
                        1000001,
                        {
                            "page_index": "1b",
                            "page_info": "kl",
                            "reference": None,
                            "span": {"start": 27, "end": 676},
                        },
                    ),
                    (
                        1000027,
                        {
                            "page_index": "2a",
                            "page_info": "lm",
                            "reference": None,
                            "span": {"start": 679, "end": 2173},
                        },
                    ),
                ],
                [
                    (
                        1000015,
                        {
                            "page_index": "1a",
                            "page_info": "kk",
                            "reference": None,
                            "span": {"start": 0, "end": 0},
                        },
                    ),
                    (
                        1000016,
                        {
                            "page_index": "1b",
                            "page_info": "",
                            "reference": None,
                            "span": {"start": 0, "end": 266},
                        },
                    ),
                ],
                [
                    (
                        1000022,
                        {
                            "page_index": "1a",
                            "page_info": "ko",
                            "reference": None,
                            "span": {"start": 0, "end": 266},
                        },
                    )
                ],
            ],
            AnnType.topic: [
                [
                    (
                        1000002,
                        {"work_id": "T1", "span": {"vol": 1, "start": 27, "end": 2046}},
                    )
                ],
                [
                    (
                        1000014,
                        {
                            "work_id": "t2",
                            "span": {"vol": 1, "start": 2046, "end": 2173},
                        },
                    )
                ],
                [
                    (
                        1000017,
                        {"work_id": "T2", "span": {"vol": 2, "start": 26, "end": 266}},
                    )
                ],
                [
                    (
                        1000023,
                        {"work_id": "T3", "span": {"vol": 3, "start": 26, "end": 243}},
                    )
                ],
                [
                    (
                        1000026,
                        {"work_id": "t4", "span": {"vol": 3, "start": 243, "end": 266}},
                    )
                ],
            ],
            AnnType.sub_topic: [
                [
                    [
                        (
                            1000003,
                            {
                                "work_id": "T1-1",
                                "span": {"vol": 1, "start": 27, "end": 1352},
                            },
                        )
                    ],
                    [
                        (
                            1000005,
                            {
                                "work_id": "T1-2",
                                "span": {"vol": 1, "start": 1352, "end": 1496},
                            },
                        )
                    ],
                    [
                        (
                            1000006,
                            {
                                "work_id": "T1-6",
                                "span": {"vol": 1, "start": 1496, "end": 2046},
                            },
                        )
                    ],
                ],
                [[]],
                [
                    [
                        (
                            1000018,
                            {
                                "work_id": "T1-8",
                                "span": {"vol": 2, "start": 26, "end": 140},
                            },
                        )
                    ],
                    [
                        (
                            1000019,
                            {
                                "work_id": "T1-9",
                                "span": {"vol": 2, "start": 140, "end": 266},
                            },
                        )
                    ],
                ],
                [[]],
                [[]],
            ],
            AnnType.sabche: [
                [(1000008, {"span": {"start": 1548, "end": 1936}})],
                [],
                [],
            ],
            AnnType.tsawa: [[(1000004, {"span": {"start": 420, "end": 739}})], [], []],
            AnnType.yigchung: [
                [],
                [],
                [(1000025, {"span": {"start": 164, "end": 241}})],
            ],
            AnnType.correction: [
                [
                    (
                        1000010,
                        {"correction": "མཆིའོ་", "span": {"start": 1838, "end": 1843}},
                    )
                ],
                [],
                [],
            ],
            AnnType.error_candidate: [
                [
                    (1000012, {"span": {"start": 2040, "end": 2042}}),
                    (1000013, {"span": {"start": 2044, "end": 2045}}),
                ],
                [],
                [],
            ],
            AnnType.peydurma: [
                [
                    (1000007, {"span": {"start": 1518, "end": 1518}}),
                    (1000009, {"span": {"start": 1624, "end": 1624}}),
                    (1000011, {"span": {"start": 1938, "end": 1938}}),
                ],
                [],
                [],
            ],
            AnnType.archaic: [[], [], []],
            AnnType.durchen: [[], [], []],
        }

        for layer in result:
            assert result[layer] == expected_result[layer]

    def test_tofu_id(self):
        formatter = HFMLFormatter()
        formatter.dirs = {}
        formatter.dirs["layers_path"] = Path("tests/data/formatter/hfml/tofu-id")
        layers = [layer.stem for layer in formatter.dirs["layers_path"].iterdir()]
        old_layers = formatter.get_old_layers(layers)
        local_id2uuid = LocalIdManager(old_layers)
        local_id2uuid.add("tsawa", "v001", 1231232)


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
            AnnType.book_title: [
                [(None, {"iscover": True, "span": {"start": 0, "end": 84}})]
            ],
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
    # TestHFMLFormatter().test_tofu_id()
    # path = Path("./tests/data/formatter/tsadra_hfml/")
    # path = Path("./output/tsadra_hfml/tsadra_hfml.opf/")

    # path = "./output/chagchen/"
    # pecha_id = 9
    # formatter = HFMLFormatter()
    # formatter.create_opf(path, pecha_id)

    # path = "./output/demo/src/P000101/OEBPS/"
    # formatter = TsadraFormatter()
    # formatter.create_opf(path, 9)
    TestTsadraFormatter().test_tsadra_formatter()
