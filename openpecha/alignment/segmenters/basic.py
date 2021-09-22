from pathlib import Path

from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.utils import get_unique_id
from openpecha.formatters.layers import Span


def get_segment_annotation(segment, char_walker):
    """Return segment annotation detail

    Args:
        segment (str): text segment
        char_walker (int): character walker

    Returns:
        dict: segment_annotation
    """
    segment_annotation = {
        get_unique_id(): {
            "span": Span(
                char_walker, char_walker + len(segment) - 1
            )  # minus one to exclude newline
        }
    }
    return segment_annotation


def get_segment_layer(segmented_text):
    """Generate segment layer from text considering each segment is seperated by two newlines

    Args:
        segmented_text (str): segmented text

    Returns:
        obj: segment layer object
    """
    segment_annotations = {}
    char_walker = 0
    segments = segmented_text.splitlines()
    for segment in segments:
        if segment:
            segment_annotation = get_segment_annotation(segment, char_walker)
            segment_annotations.update(segment_annotation)
        char_walker += len(segment) + 1

    segment_layer = Layer(
        id=get_unique_id(),
        annotation_type="Segment",
        revision="00001",
        annotations=segment_annotations,
    )
    return segment_layer


def create_opf(segmented_text_path, opf_path):
    """Create opf of segmented text where segment seperator is two new lines

    Args:
        segmented_text_path (str): segmented text path
        opf_path (str): path where you want to save opf
    """
    opf = OpenPechaFS(opf_path=opf_path)
    segmented_text = Path(segmented_text_path).read_text(encoding="utf-8")
    layers = {"v001": {LayerEnum.segment: get_segment_layer(segmented_text)}}
    bases = {"v001": segmented_text}
    opf.layers = layers
    opf.base = bases
    opf.save_base()
    opf.save_layers()
