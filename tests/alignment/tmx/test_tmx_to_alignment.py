import tempfile
from pathlib import Path

from openpecha import config
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


def get_annotations(source_pecha, target_pecha):
    
    for _id, source_segment_yml in source_pecha.layers.items():
        source_base_id = _id
        for _, _value in source_segment_yml.items():
            source_annotations = _value.annotations
    for id_, target_segment_yml in target_pecha.layers.items():
        target_base_id = id_
        for _, value_ in target_segment_yml.items():
            target_annotations = value_.annotations
            
    return source_annotations, target_annotations


def get_text(
    annotation_ids,
    source_pecha,
    target_pecha,
    source_annotations,
    target_annotations,
):
    for _, _text in source_pecha.bases.items():
        source_base = _text
    for _, text_ in target_pecha.bases.items():
        target_base = text_
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
    config.PECHAS_PATH = Path(tempfile.gettempdir()) / "pechas"

    tmx_path = Path("./tests/data/alignment/tmx/input.tmx")
    source_pecha, target_pecha, source_metadata = create_opf_from_tmx(
        tmx_path
    )

    obj = TMXAlignment()
    title = tmx_path.stem
    origin_type = "translation"
    alignment_path = obj.create_alignment_repo(
        source_pecha, target_pecha, title, source_metadata, origin_type
    )

    source_annotations, target_annotations = get_annotations(
        source_pecha, target_pecha
    )

    alignment_yml = load_yaml(
        Path(alignment_path / f"{alignment_path.stem}.opa" / "Alignment.yml")
    )
    segment_pairs = alignment_yml["segment_pairs"]
    annotation_ids = get_segment_pairs_annotation_ids(
        segment_pairs, source_pecha.pecha_id, target_pecha.pecha_id
    )

    opf_text = get_text(
        annotation_ids,
        source_pecha,
        target_pecha,
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

    alignment_yml = load_yaml(
        alignment_path / f"{alignment_path.stem}.opa" / "Alignment.yml"
    )
    segment_source = alignment_yml["segment_sources"]
    for uid, segment_info in segment_source.items():
        if segment_info["relation"] == "source":
            source_pecha_id = uid
        elif segment_info["relation"] == "target":
            target_pecha_id = uid

    # assert source_pecha_path.stem == source_pecha_id
    # assert target_pecha_path.stem == target_pecha_id



if __name__ == "__main__":
    test_tmx_to_alignment()