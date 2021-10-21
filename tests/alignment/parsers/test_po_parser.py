import shutil
import tempfile
from pathlib import Path

from openpecha.alignment.parsers.po import update_alignment_from_po
from openpecha.utils import load_yaml


def get_span(segment):
    num = 0
    curr_span = {}
    final_span = {}
    annotations = segment["annotations"]
    for _, annotation in annotations.items():
        curr_span[num] = annotation["span"]
        final_span.update(curr_span)
        curr_span = {}
        num += 1
    return final_span


def test_update_alignment_from_po():
    po_path = Path("./tests/data/alignment/parsers/po/transifex_output.po")
    test_alignment_path = Path(
        "./tests/data/alignment/parsers/po/85b3e1c711244059a65911602f724a38"
    )
    alignment_path = (
        Path(tempfile.gettempdir()) / "pechas" / "85b3e1c711244059a65911602f724a38"
    )
    shutil.copytree(str(test_alignment_path), str(alignment_path), dirs_exist_ok=True)
    target_pecha_path = update_alignment_from_po(po_path, alignment_path, publish=False)
    target_pecha_id = target_pecha_path.stem
    target_segment = load_yaml(
        target_pecha_path / f"{target_pecha_id}.opf" / "layers/0001/Segment.yml"
    )
    target_span = get_span(target_segment)

    expected_target_segment = load_yaml(
        Path("./tests/data/alignment/tmx/expected_target_segment.yml")
    )
    expected_target_span = get_span(expected_target_segment)

    assert target_span == expected_target_span
