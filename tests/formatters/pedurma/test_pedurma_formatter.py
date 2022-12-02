from pathlib import Path

from openpecha.core.layer import LayerEnum
from openpecha.formatters import PedurmaFormatter


def test_pedurma_formatter():
    preview_text = (Path(__file__).parent / "data" / "preview_text.txt").read_text(
        encoding="utf-8"
    )
    formatter = PedurmaFormatter()
    formatter.build_layers(preview_text)
    layers = formatter.get_result()
    expected_layers = {
        LayerEnum.topic: [],
        LayerEnum.sub_topic: [],
        LayerEnum.pagination: [
            [
                (
                    "",
                    {
                        "imgnum": "42",
                        "reference": None,
                        "span": {"start": 1, "end": 120},
                    },
                ),
                (
                    "",
                    {
                        "imgnum": "43",
                        "reference": None,
                        "span": {"start": 122, "end": 361},
                    },
                ),
                (
                    "",
                    {
                        "imgnum": "44",
                        "reference": None,
                        "span": {"start": 363, "end": 538},
                    },
                ),
            ]
        ],
        LayerEnum.pedurma_note: [
            [
                (
                    "",
                    {
                        "span": {"start": 14, "end": 18},
                        "variants": {
                            "«པེ་»": "མཚན་བྱང་འདི་ལྟར་བཀོད།",
                            "«སྣར་»": "",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»མཚན་བྱང་འདི་ལྟར་བཀོད།>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 33, "end": 40},
                        "variants": {
                            "«པེ་»": "ཏྲ་ན་",
                            "«སྣར་»": "ཏྲ་ན་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»ཏྲ་ན་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 57, "end": 61},
                        "variants": {
                            "«པེ་»": "ཀྱི་",
                            "«སྣར་»": "ཀྱི་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»ཀྱི་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 127, "end": 130},
                        "variants": {
                            "«པེ་»": "ཅེས་",
                            "«སྣར་»": "ཅེས་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»ཅེས་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 136, "end": 140},
                        "variants": {
                            "«པེ་»": "ཀྱི་",
                            "«སྣར་»": "ཀྱི་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "གི་",
                        },
                        "collation_note": "<«ཅོ་»གི་«པེ་»«སྣར་»ཀྱི་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 204, "end": 207},
                        "variants": {
                            "«པེ་»": "ཟད་",
                            "«སྣར་»": "ཟད་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»ཟད་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 226, "end": 233},
                        "variants": {
                            "«པེ་»": "སྲེག",
                            "«སྣར་»": "སྲེག",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»སྲེག>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 321, "end": 324},
                        "variants": {
                            "«པེ་»": "",
                            "«སྣར་»": "འཆི་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«སྣར་»འཆི་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 363, "end": 365},
                        "variants": {
                            "«པེ་»": "གཅིག",
                            "«སྣར་»": "གཅིག",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»གཅིག>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 418, "end": 428},
                        "variants": {
                            "«པེ་»": "བྲམ་ཟེ་",
                            "«སྣར་»": "བྲམ་ཟེ་",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»«སྣར་»བྲམ་ཟེ་>",
                    },
                ),
                (
                    "",
                    {
                        "span": {"start": 496, "end": 504},
                        "variants": {
                            "«པེ་»": "ཛ་ར་དན་",
                            "«སྣར་»": "",
                            "«སྡེ»": "",
                            "«ཅོ་»": "",
                        },
                        "collation_note": "<«པེ་»ཛ་ར་དན་>",
                    },
                ),
            ]
        ],
    }
    # assert expected_layers == layers


def test_get_base():
    expected_base = (Path(__file__).parent / "data" / "expected_base.txt").read_text(
        encoding="utf-8"
    )
    preview_text = (Path(__file__).parent / "data" / "preview_text.txt").read_text(
        encoding="utf-8"
    )
    formatter = PedurmaFormatter()
    base_text = formatter.base_extract(preview_text)
    assert expected_base == base_text
