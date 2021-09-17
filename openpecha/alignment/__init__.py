from pathlib import Path

from openpecha.cli import download_pecha
from openpecha.utils import load_yaml


class Alignment:
    def __init__(self, id, title, alignment_type, segment_sources, segment_pairs):
        self.id = id
        self.title = title
        self.alignment_type = alignment_type
        self.segment_sources = segment_sources
        self.segment_pairs = segment_pairs

    def get_segment_src_paths(self):
        segment_src_pecha_paths = {}
        segment_src_pechas = self.segment_sources.keys()
        for segment_src_pecha in segment_src_pechas:
            segment_src_pecha_paths[segment_src_pecha] = download_pecha(
                segment_src_pecha
            )
        return segment_src_pecha_paths

    def get_segment_layer(self, pecha_id, pecha_path):
        try:
            segment_layer = load_yaml(
                (Path(pecha_path) / f"{pecha_id}.opf/layers/Segment.yml")
            )
            segment_annotations = list(segment_layer["annotations"])
            return segment_annotations
        except Exception:
            return []

    def get_segment_annotations(self, segment_src_paths):
        segment_annotations = {}
        for segment_src_pecha_id, segment_src_pecha_path in segment_src_paths.items():
            segment_annotations[segment_src_pecha_id] = self.get_segment_layer(
                segment_src_pecha_id, segment_src_pecha_path
            )
        return segment_annotations

    def longest_segment(self, segment_annotations):
        src = max(segment_annotations, key=lambda k: len(segment_annotations[k]))
        return segment_annotations[src]

    def get_cur_segment_pairs(self, segment_annotations, segment_walker):
        cur_segment_pairs = {}
        for src, segment_ann in segment_annotations.items():
            try:
                cur_segment_pairs[src] = segment_ann[segment_walker]
            except Exception:
                cur_segment_pairs[src] = ""
        return cur_segment_pairs

    def generate_segment_pairs(self, segment_src_paths):
        segment_pairs = {}
        segment_annotations = self.get_segment_annotations(segment_src_paths)
        longest_segment_ann = self.longest_segment(segment_annotations)
        for segment_walker, segment_id in enumerate(longest_segment_ann):
            cur_segment_pairs = self.get_cur_segment_pairs(
                segment_annotations, segment_walker
            )
            segment_pairs[f"{int(segment_walker):04}"] = cur_segment_pairs
            cur_segment_pairs = {}
        return segment_pairs

    def export(self, format=None):
        pass
