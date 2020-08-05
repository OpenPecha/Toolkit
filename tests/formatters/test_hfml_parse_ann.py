from collections import defaultdict
from pathlib import Path

import pytest

from openpecha.formatters import HFMLFormatter
from openpecha.formatters.layers import *


@pytest.fixture()
def formatter():
    """Return HFMLFormatter object."""
    from openpecha.formatters.layers import HFML_ANN_PATTERN

    config = {"ann_patterns": HFML_ANN_PATTERN}
    return HFMLFormatter(config=config)


@pytest.fixture()
def one_vol_test_data():
    m_text = Path("tests/data/formatter/hfml/v001.txt").read_text()
    base_id = "v001"
    expected = defaultdict(lambda: defaultdict(list))
    expected[AnnType.pecha_title][base_id].append((":", OnlySpan(Span(0, 3))))
    expected[AnnType.correction][base_id].append(
        (":", Correction(Span(8, 9), correction="ཁ"))
    )
    return m_text, base_id, expected


def evaluate_layers(result, expected):
    for layer_name in expected:
        result_layer = result[layer_name]
        expected_layer = expected[layer_name]
        for base_id in expected_layer:
            for (r_id, r_ann), (e_id, e_ann) in zip(
                result_layer[base_id], expected_layer[base_id]
            ):
                assert r_id == e_id
                for attr_name in e_ann:
                    if attr_name == "span":
                        for span_attr_name in e_ann[attr_name]:
                            assert (
                                r_ann[attr_name][span_attr_name]
                                == e_ann[attr_name][span_attr_name]
                            )
                    else:
                        assert r_ann[attr_name] == e_ann[attr_name]


def test_parse_ann_one_vol(formatter, one_vol_test_data):
    m_text, base_id, expected = one_vol_test_data

    formatter.parse_ann(m_text, base_id)

    evaluate_layers(formatter.layers, expected)
