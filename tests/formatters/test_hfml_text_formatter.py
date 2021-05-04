import json
import yaml
from pathlib import Path

import pytest

from openpecha.core.layer import LayersEnum
from openpecha.formatters import HFMLTextFromatter
from openpecha.formatters.formatter import LocalIdManager
from openpecha.formatters.layers import AnnType


def from_yaml(self, yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

def get_expected_base_text():
    expected_base = {}
    base_paths = list(Path('./data/formatter/text_formatter/expected_base').iterdir()).sort()
    for base_path in base_paths:
        expected_base[base_path.stem] = base_path.read_text(encoding='utf-8')
    return expected_base


def test_update_base_text():
    text_formatter = HFMLTextFromatter()
    pecha_opf_path = Path('./data/formatter/text_formatter/P000002.opf')
    text_opf_path = Path('./data/formatter/text_formatter/D1118.opf')
    pecha_idx = from_yaml(pecha_opf_path / "index.yml")
    text_id = "D1118"
    expected_base_texts = get_expected_base_text()
    for vol_id, base_text in text_formatter.update_base_text(pecha_opf_path, text_opf_path, pecha_idx, text_id):
        assert expected_base_texts[vol_id] == base_text

def test_update_layer():
    text_formatter = HFMLTextFromatter()
    cur_vol_pecha_layer = from_yaml(Path('./data/formatter/text_formatter/P000002.opf/layers/v001/Pagination.yml'))
    cur_vol_text_layer = from_yaml(Path('./data/formatter/text_formatter/D1118.opf/layers/v001/Pagination.yml'))
    cur_vol_offset = 20
    expected_layer = from_yaml(Path('./data/formatter/text_formatter/expected_layer.yml'))
    new_layer = text_formatter.get_new_layer(cur_vol_pecha_layer, cur_vol_text_layer, cur_vol_offset)
    assert expected_layer == new_layer