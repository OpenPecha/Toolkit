from pathlib import Path

import pytest

from openpecha.formatters import HFMLFormatter
from openpecha.formatters.hfml import ANN_PATTERN
from openpecha.formatters.layers import AnnType, _attr_names


@pytest.fixture()
def get_expected_one_vol():
    anns = {
        AnnType.peydurma: {
            "v001": [
                (
                    None,
                    {
                        _attr_names.NOTE: "kk",
                        _attr_names.SPAN: {_attr_names.START: 5, _attr_names.END: 8},
                    },
                ),
                (
                    None,
                    {
                        _attr_names.NOTE: "dd",
                        _attr_names.SPAN: {_attr_names.START: 10, _attr_names.END: 13},
                    },
                ),
            ]
        }


@pytest.fixture()
def formatter():
    """Return HFMLFormatter object."""
    from openpecha.formatters.hfml import ANN_PATTERN

    config = {"ann_patterns": ANN_PATTERN}
    return HFMLFormatter(config=config)


def test_parse_ann_one_vol(formatter):
    m_text = Path("tests/data/formatter/hfml/kangyur_01.txt").read_text()
    base_id = "v001"

    expected = {}

    result = formatter.parse_ann(m_text, base_id)
