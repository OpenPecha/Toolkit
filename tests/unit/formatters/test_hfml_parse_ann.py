from pathlib import Path

import pytest

from openpecha.formatters import HFMLFormatter


@pytest.fixture()
def formatter():
    """Return HFMLFormatter object."""
    return HFMLFormatter()


def test_parse_ann_one_vol():
    formatter = HFMLFormatter()
    input_hfml = Path("tests/data/formatter/hfml/new/input.txt").read_text()
    excepted = {}

    result = formatter.parse_ann(input_hfml)
