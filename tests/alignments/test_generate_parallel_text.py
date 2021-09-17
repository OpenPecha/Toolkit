from pathlib import Path

import pytest

from openpecha.alignment.generate import get_segment_pairs


def test_get_segment_pair():
    segment_src_paths = {
        "CJKBO001": "./tests/data/alignment/CJKBO001",
        "CJKEN001": "./tests/data/alignment/CJKEN001",
        "CJKZH001": "./tests/data/alignment/CJKZH001",
    }
    segment_pairs = {
        "0001": {
            "CJKBO001": "55b8bf66c8294e6d9d173ff2835dfc7d",
            "CJKEN001": "6fd51723631c4c79a89faeb2c3b0b9b2",
            "CJKZH001": "b36a339aab91456d96f781d4ae073f82",
        },
        "0002": {
            "CJKBO001": "44ad25f4369b40bb8a81f895316151de",
            "CJKEN001": "70703b677531468f97c475aae29f0e2f",
            "CJKZH001": "eebb8f0fb0a24fef8802444b3b83897b",
        },
        "0003": {
            "CJKBO001": "c0d79820078745e2bc4a913880a64608",
            "CJKEN001": "9722961a3e7549a380caa9b8c8eea1a3",
            "CJKZH001": "1caa4b71e036448884a4498fec29c173",
        },
        "0004": {
            "CJKBO001": "6c90138bbe4b42fbb0a376957e8da2fd",
            "CJKEN001": "b463b36bfa7d42ebb9d6b8ebe22ca332",
            "CJKZH001": "f3924279964e4858829d43d427be94ef",
        },
        "0005": {
            "CJKBO001": "587c750ca8db4693bc25a2d450fdce16",
            "CJKEN001": "c2cf568e504c4bc4b1ac444104d5e6a6",
            "CJKZH001": "55dfca0411ab4c2f9128e77eee70f53f",
        },
    }
    expected_parallel_text = Path(
        "./tests/data/alignment/expected_parallel_text.txt"
    ).read_text(encoding="utf-8")
    parallel_text = get_segment_pairs(segment_src_paths, segment_pairs)
    assert expected_parallel_text == parallel_text
