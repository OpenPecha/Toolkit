from pathlib import Path

from openpecha.core.layer import LayerEnum
from openpecha.formatters import HFMLFormatter
from openpecha.formatters.formatter import LocalIdManager


class TestHFMLFormatter:
    def test_get_base_text(self):

        m_text = (Path(__file__).parent / "data" / "kangyur_01.txt").read_text(encoding='utf-8')
        formatter = HFMLFormatter()

        text = formatter.text_preprocess(m_text)
        formatter.build_layers(text, len([text]))
        result = formatter.get_base_text()

        expected = (Path(__file__).parent / "data" / "kangyur_base.txt").read_text(encoding='utf-8')

        assert result == expected

    def test_build_layers(self):
        m_text1 = (Path(__file__).parent / "data" / "kangyur_01.txt").read_text(encoding='utf-8')
        m_text2 = (Path(__file__).parent / "data" / "kangyur_02.txt").read_text(encoding='utf-8')
        m_text3 = (Path(__file__).parent / "data" / "kangyur_03.txt").read_text(encoding='utf-8')
        formatter = HFMLFormatter()

        text1 = formatter.text_preprocess(m_text1)
        text2 = formatter.text_preprocess(m_text2)
        text3 = formatter.text_preprocess(m_text3)
        texts = [text1, text2, text3]
        for text in texts:
            result = formatter.build_layers(text, len(texts))

        result = formatter.get_result()
        expected_result = {
            LayerEnum.book_title: [[], [], []],
            LayerEnum.book_number: [[], [], []],
            LayerEnum.author: [[], [], []],
            LayerEnum.poti_title: [
                [(None, {"span": {"start": 0, "end": 24}})],
                [(None, {"span": {"start": 0, "end": 24}})],
                [(None, {"span": {"start": 0, "end": 24}})],
            ],
            LayerEnum.chapter: [[(None, {"span": {"start": 98, "end": 125}})], [], []],
            LayerEnum.citation: [
                [],
                [
                    (1000020, {"span": {"start": 164, "end": 202}}),
                    (1000021, {"span": {"start": 204, "end": 241}}),
                ],
                [(1000024, {"span": {"start": 97, "end": 162}})],
            ],
            LayerEnum.pagination: [
                [
                    (
                        1000000,
                        {
                            "imgnum": "1",
                            "reference": "kk",
                            "span": {"start": 0, "end": 24},
                        },
                    ),
                    (
                        1000001,
                        {
                            "imgnum": "2",
                            "reference": "kl",
                            "span": {"start": 27, "end": 676},
                        },
                    ),
                    (
                        1000027,
                        {
                            "imgnum": "3",
                            "reference": "lm",
                            "span": {"start": 679, "end": 2173},
                        },
                    ),
                ],
                [
                    (
                        1000015,
                        {
                            "imgnum": "1",
                            "reference": "kk",
                            "span": {"start": 0, "end": 0},
                        },
                    ),
                    (
                        1000016,
                        {
                            "imgnum": "2",
                            "reference": "",
                            "span": {"start": 0, "end": 266},
                        },
                    ),
                ],
                [
                    (
                        1000022,
                        {
                            "imgnum": "1",
                            "reference": "ko",
                            "span": {"start": 0, "end": 266},
                        },
                    )
                ],
            ],
            LayerEnum.topic: [
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
            LayerEnum.sub_topic: [
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
            LayerEnum.sabche: [
                [(1000008, {"span": {"start": 1548, "end": 1936}})],
                [],
                [],
            ],
            LayerEnum.tsawa: [
                [(1000004, {"span": {"start": 420, "end": 739}})],
                [],
                [],
            ],
            LayerEnum.yigchung: [
                [],
                [],
                [(1000025, {"span": {"start": 164, "end": 241}})],
            ],
            LayerEnum.correction: [
                [
                    (
                        1000010,
                        {"correction": "མཆིའོ་", "span": {"start": 1838, "end": 1843}},
                    )
                ],
                [],
                [],
            ],
            LayerEnum.error_candidate: [
                [
                    (1000012, {"span": {"start": 2040, "end": 2042}}),
                    (1000013, {"span": {"start": 2044, "end": 2045}}),
                ],
                [],
                [],
            ],
            LayerEnum.peydurma: [
                [
                    (1000007, {"span": {"start": 1518, "end": 1518}}),
                    (1000009, {"span": {"start": 1624, "end": 1624}}),
                    (1000011, {"span": {"start": 1938, "end": 1938}}),
                ],
                [],
                [],
            ],
            LayerEnum.archaic: [[], [], []],
            LayerEnum.durchen: [[], [], []],
        }

        # for layer in result:
        #     assert result[layer] == expected_result[layer]

    def test_tofu_id(self):
        formatter = HFMLFormatter()
        formatter.dirs = {}
        formatter.dirs["layers_path"] = Path(__file__).parent / "data" / "tofu-id"
        layers = [layer.stem for layer in formatter.dirs["layers_path"].iterdir()]
        old_layers = formatter.get_old_layers(layers)
        local_id2uuid = LocalIdManager(old_layers)
        local_id2uuid.add("tsawa", "v001", 1231232)
