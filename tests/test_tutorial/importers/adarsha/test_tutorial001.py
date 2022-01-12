from pathlib import Path

from docs_src.importers.adarsha.tutorial001 import output_path,work

def test_base():
    with open(f"{output_path}/expected_base.txt", "r") as f:
            base_text = f.read()

    with open(f"{output_path}/{work[0]}/{work[0]}.opf/base/001.txt") as f:
            test_base_text = f.read()

    assert base_text == test_base_text
