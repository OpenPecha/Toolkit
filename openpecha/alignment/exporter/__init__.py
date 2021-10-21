from logging import NOTSET
from pathlib import Path

from openpecha.utils import download_pecha, load_yaml


class Exporter:
    def __init__(self, alignment_path) -> None:
        self.alignment_path = alignment_path if alignment_path else None
        self.alignment = load_yaml(self.alignment_path) if self.alignment_path else {}

    def get_base_layer(self, pecha_id, pecha_path=None):
        """Return base text of the pecha

        Args:
            pecha_id (st): pecha uuid
            pecha_path (str, optional): path of the pecha. Defaults to None.

        Returns:
            [str]: base text of the pecha
        """
        base = ""
        if pecha_path is None:
            pecha_path = download_pecha(pecha_id)
        base = (pecha_path / f"{pecha_id}.opf" / "base" / "0001.txt").read_text(
            encoding="utf-8"
        )
        return base

    def get_segment_layer(self, pecha_id, pecha_path):
        """Return src pecha's segment annotations detail from segment layer

        Args:
            pecha_id (str): pecha id
            pecha_path (str): pecha path

        Returns:
            dict: segment annotations detail
        """
        if pecha_path is None:
            pecha_path = download_pecha(pecha_id)
        try:
            segment_layer = load_yaml(
                (pecha_path / f"{pecha_id}.opf" / "layers" / "0001" / "Segment.yml")
            )
            segment_annotations = segment_layer["annotations"]
            return segment_annotations
        except Exception:
            return {}

    def get_segment(self, segment_ann, base_text):
        """Extract segment text and return

        Args:
            segment_ann (dict): segment annotation detail
            base_text (str): base text of the segment

        Returns:
            str: segment text from base text
        """
        segment_text = ""
        if segment_ann:
            segment_start = segment_ann["span"]["start"]
            segment_end = segment_ann["span"]["end"]
            segment_text = base_text[segment_start : segment_end + 1]
        return segment_text

    def get_segment_texts(self, pecha_id, pecha_path=None):
        segment_texts = {}
        if pecha_path is None:
            pecha_path = download_pecha(pecha_id)
        base_text = self.get_base_layer(pecha_id, pecha_path)
        segment_layer = self.get_segment_layer(pecha_id, pecha_path)
        for pair_id, segment_pair in self.alignment["segment_pairs"].items():
            segment_id = segment_pair.get(pecha_id, "")
            segment_ann = segment_layer.get(segment_id, {})
            if segment_ann:
                segment_texts[pair_id] = self.get_segment(segment_ann, base_text)
        return segment_texts

    def export(self):
        raise NotImplementedError
