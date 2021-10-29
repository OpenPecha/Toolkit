import tempfile
from pathlib import Path

from openpecha import config
from openpecha.alignment.tmx.create_opf import create_opf_from_tmx
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


def test_create_tmx_to_opf():
    config.PECHAS_PATH = Path(tempfile.gettempdir()) / "pechas"
    tmx_path = Path("./tests/data/alignment/tmx/input.tmx")
    source_pecha_path, target_pecha_path, _ = create_opf_from_tmx(tmx_path)

    source_pecha_id = source_pecha_path.stem
    target_pecha_id = target_pecha_path.stem

    source_segment = load_yaml(
        (source_pecha_path / f"{source_pecha_id}.opf" / "layers/0001/Segment.yml")
    )
    target_segment = load_yaml(
        (target_pecha_path / f"{target_pecha_id}.opf" / "layers/0001/Segment.yml")
    )
    source_span = get_span(source_segment)
    target_span = get_span(target_segment)

    expected_source_segment = load_yaml(
        Path("./tests/data/alignment/tmx/expected_source_segment.yml")
    )
    expected_target_segment = load_yaml(
        Path("./tests/data/alignment/tmx/expected_target_segment.yml")
    )
    expected_source_span = get_span(expected_source_segment)
    expected_target_span = get_span(expected_target_segment)

    assert source_span == expected_source_span
    assert target_span == expected_target_span
