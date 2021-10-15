from pathlib import Path

import pytest

from openpecha.alignment import Alignment


@pytest.fixture(scope="module")
def alignment_path():
    alignment_id = "b696df2dbe314e8a87881a2bc391d0d5"
    return (
        Path.cwd()
        / "tests"
        / "data"
        / "alignment"
        / alignment_id
        / f"{alignment_id}.opa"
        / "Alignment.yml"
    )
