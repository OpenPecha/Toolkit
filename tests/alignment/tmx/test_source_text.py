import tempfile
from pathlib import Path

from openpecha import config
from openpecha.alignment.tmx.create_opf import create_alignment_from_source_text


def test_create_alignment_from_source_text():
    
    text_path = Path("./tests/data/alignment/tmx/new_text.txt")
    source_metadata = {
        'title': "this is title"
    }
    alignment_path = create_alignment_from_source_text(text_path, 'bo', source_metadata, publish=False)
    assert alignment_path


if __name__ == "__main__":
    test_create_alignment_from_source_text()