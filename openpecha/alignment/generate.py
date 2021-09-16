from pathlib import Path

from openpecha import alignment
from openpecha.alignment import Alignment
from openpecha.utils import load_yaml


def get_src_bases(src_paths):
    src_bases = {}
    for src_name, src_path in src_paths.items():
        src_bases[src_name] = (Path(src_path) / f"{src_name}/bases/0001.txt").read_text(
            encoding="utf-8"
        )
    return src_bases


def get_segment_layer(self, pecha_id, pecha_path):
    try:
        segment_layer = load_yaml((Path(pecha_path) / f"{pecha_id}/layers/Segment.yml"))
        segment_annotations = segment_layer["annotations"]
        return segment_annotations
    except Exception:
        return {}


def get_segment_annotations(self, segment_src_paths):
    segment_annotations = {}
    for segment_src_pecha_id, segment_src_pecha_path in segment_src_paths.items():
        segment_annotations[segment_src_pecha_id] = self.get_segment_layer(
            segment_src_pecha_id, segment_src_pecha_path
        )
    return segment_annotations


def get_segment(segment_ann, src_bases, segment_src):
    segment_text = ""
    if segment_ann:
        src_base = src_bases[segment_src]
        segment_start = segment_ann["span"]["start"]
        segment_end = segment_ann["span"]["end"]
        segment_text = src_base[segment_start:segment_end]
    return segment_text


def get_segment_text(segment_annotations, src_bases, segment_pair):
    segment_text = ""
    for segment_src, segment_id in segment_pair.items():
        segment_ann = segment_annotations[segment_src].get(segment_id, {})
        segment_text += get_segment(segment_ann, src_bases, segment_src) + "\n"
    return segment_text


def get_segment_pairs(segment_src_paths, segment_pairs):
    alignment_text = ""
    segment_annotations = get_segment_annotations(segment_src_paths)
    src_bases = get_src_bases(segment_src_paths)
    for segmetn_id, segment_pair in segment_pairs.items():
        alignment_text += (
            f"{get_segment_text(segment_annotations, src_bases, segment_pair)}\n\n"
        )
    return alignment_text
