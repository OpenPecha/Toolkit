from pathlib import Path

from docs_src.importers.hfml.tutorial001 import result


def test_hfml_base():
    output_fn = Path("tests") / "formatters" / "hfml" / "data" / "kangyur_base.txt"

    expected = output_fn.read_text()

    assert result == expected
