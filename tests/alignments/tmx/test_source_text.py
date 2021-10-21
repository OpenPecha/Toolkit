from pathlib import Path

from openpecha.alignment.tmx.create_opf import create_alignment_from_source_text


def test_create_alignment_from_source_text():
    text_path = Path("./tests/data/alignment/tmx/new_text.txt")
    title = "this is title"
    alignment_path = create_alignment_from_source_text(text_path, title, publish=False)
    assert alignment_path
