from pathlib import Path

from openpecha.alignment.parsers.tmx import parse_tmx
from openpecha.alignment.tmx import TMXAlignment
from openpecha.alignment.tmx.create_opf import create_opf_from_tmx
from openpecha.utils import load_yaml


def get_segment_pairs_annotation_ids(segment_pairs, source_pecha_id, target_peccha_id):
    curr_annot = {}
    final_annot = {}
    num = 0
    for _, segment_pair in segment_pairs.items():
        src_annot = segment_pair[source_pecha_id]
        tar_annot = segment_pair[target_peccha_id]
        curr_annot[num] = {"src": src_annot, "tar": tar_annot}
        final_annot.update(curr_annot)
        curr_annot = {}
        num += 1
    return final_annot


def get_annotations(source_pecha_path, target_pecha_path):
    source_yml = load_yaml(
        Path(
            source_pecha_path
            / f"{source_pecha_path.stem}.opf"
            / "layers/0001/Segment.yml"
        )
    )
    target_yml = load_yaml(
        Path(
            target_pecha_path
            / f"{target_pecha_path.stem}.opf"
            / "layers/0001/Segment.yml"
        )
    )
    source_annotations = source_yml["annotations"]
    target_annotations = target_yml["annotations"]
    return source_annotations, target_annotations


def get_text(
    annotation_ids,
    source_pecha_path,
    target_pecha_path,
    source_annotations,
    target_annotations,
):
    source_base = Path(
        source_pecha_path / f"{source_pecha_path.stem}.opf" / "base/0001.txt"
    ).read_text(encoding="utf-8")
    target_base = Path(
        target_pecha_path / f"{target_pecha_path.stem}.opf" / "base/0001.txt"
    ).read_text(encoding="utf-8")
    curr_text = {}
    final_text = {}
    for num in range(0, 2):
        src_annot_id = annotation_ids[num]["src"]
        tar_annot_id = annotation_ids[num]["tar"]
        src_start = source_annotations[src_annot_id]["span"]["start"]
        src_end = source_annotations[src_annot_id]["span"]["end"]
        tar_start = target_annotations[tar_annot_id]["span"]["start"]
        tar_end = target_annotations[tar_annot_id]["span"]["end"]
        source_text = source_base[src_start : src_end + 1]
        target_text = target_base[tar_start : tar_end + 1]
        curr_text[num] = {"src": source_text, "tar": target_text}
        final_text.update(curr_text)
        curr_text = {}
    return final_text


def test_tmx_to_alignment():
    tmx_path = Path("./tests/data/alignment/tmx/input.tmx")
    source_pecha_path, target_pecha_path, source_metadata = create_opf_from_tmx(
        tmx_path
    )

    obj = TMXAlignment()
    title = tmx_path.stem
    origin_type = "translation"
    alignment_path = obj.create_alignment_repo(
        source_pecha_path, target_pecha_path, title, source_metadata, origin_type
    )

    source_annotations, target_annotations = get_annotations(
        source_pecha_path, target_pecha_path
    )

    alignment_yml = load_yaml(
        Path(alignment_path / f"{alignment_path.stem}.opa" / "Alignment.yml")
    )
    segment_pairs = alignment_yml["segment_pairs"]
    annotation_ids = get_segment_pairs_annotation_ids(
        segment_pairs, source_pecha_path.stem, target_pecha_path.stem
    )

    opf_text = get_text(
        annotation_ids,
        source_pecha_path,
        target_pecha_path,
        source_annotations,
        target_annotations,
    )

    alignment = Path("./tests/data/alignment/tmx/expected_alignment.txt").read_text(
        encoding="utf-8"
    )
    expected_segment_pairs = alignment.splitlines()
    for num, expected_segment_pair in enumerate(expected_segment_pairs):
        expected_segment_src, expected_segment_tar = expected_segment_pair.split("  ")
        src_seg = opf_text[num]["src"]
        tar_seg = opf_text[num]["tar"]
        assert expected_segment_src == src_seg
        assert expected_segment_tar == tar_seg
