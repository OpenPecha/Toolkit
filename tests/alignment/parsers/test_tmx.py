from pathlib import Path

from openpecha.alignment.parsers.tmx import parse_tmx
from openpecha.utils import load_yaml


def test_parse_tmx():
    expected_src_text = ""
    expected_tar_text = ""
    tmx_path = Path("./tests/data/alignment/tmx/input.tmx")
    src_text, tar_text, source_metadata = parse_tmx(tmx_path)
    expected_texts = Path(
        "./tests/data/alignment/parsers/tmx/expected_tmx_parsers_output_text.txt"
    ).read_text(encoding="utf-8")
    expected_source_metadata_yml = load_yaml(
        Path(
            "./tests/data/alignment/parsers/tmx/expected_tmx_parsers_source_metadata.yml"
        )
    )
    expected_texts = expected_texts.splitlines()
    for num, text in enumerate(expected_texts):
        if num < 2:
            expected_src_text += text + "\n"
        else:
            expected_tar_text += text + "\n"
    expected_source_metadata = expected_source_metadata_yml["source_metadata"]
    assert expected_src_text == src_text
    assert expected_tar_text == tar_text
    assert expected_source_metadata == source_metadata
