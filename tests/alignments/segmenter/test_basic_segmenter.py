from pathlib import Path

from openpecha.alignment.segmenters.basic import get_segment_layer
from openpecha.utils import load_yaml


def test_get_segment_layer():
    segmented_text = Path("./tests/data/alignment/segmented_text.txt").read_text()
    expected_seg_annotations = load_yaml(
        Path("./tests/data/alignment/expected_seg_ann.yml")
    )
    segment_layer = get_segment_layer(segmented_text)
    segment_annotations = segment_layer.annotations
    for seg_ann_id, expected_ann_id in zip(
        segment_annotations, expected_seg_annotations
    ):
        assert (
            segment_annotations[seg_ann_id] == expected_seg_annotations[expected_ann_id]
        )
