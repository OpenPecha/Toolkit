from pathlib import Path

import pytest

from openpecha.alignment import *


def test_create_alignment():
    items = {
        "CJKBO001": {"alignment_type": "translation", "lang": "bo"},
        "CJKEN001": {"alignment_type": "translation", "lang": "en"},
        "CJKZH001": {"alignment_type": "translation", "lang": "zh"},
    }
    segment_src_paths = {
        "CJKBO001": "./tests/data/alignment/CJKBO001",
        "CJKEN001": "./tests/data/alignment/CJKEN001",
        "CJKZH001": "./tests/data/alignment/CJKZH001",
    }
    alignment = Alignment(id="00003", title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ་")
    expected_path = Path("./tests/data/alignment/alignment.yml")
    alignment_yml_path = alignment.create_alignment(
        items, segment_src_paths, output_path="./tests/data/alignment/alignment.yml"
    )
    assert alignment_yml_path == expected_path
    alignment_yml_path.unlink()
