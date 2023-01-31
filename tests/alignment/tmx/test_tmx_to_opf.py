import tempfile
from pathlib import Path

from openpecha import config
from openpecha.alignment.tmx.create_opf import create_opf_from_tmx
from openpecha.utils import load_yaml


def get_span(annotations, type=None):
    num = 0
    curr_span = {}
    final_span = {}
    for _, annotation in annotations.items():
        if type == "expected":
            curr_span[num] = annotation["span"]
        else:
            curr_span[num] = {
                'start': annotation.span.start,
                'end': annotation.span.end
            }
        final_span.update(curr_span)
        curr_span = {}
        num += 1
    return final_span


def test_create_tmx_to_opf():

    tmx_path = Path("./tests/data/alignment/tmx/input.tmx")
    source_pecha, target_pecha, _ = create_opf_from_tmx(tmx_path)

    for _, source_segment_yml in source_pecha.layers.items():
            for _, _value in source_segment_yml.items():
                source_annotations = _value.annotations
    for _, target_segment_yml in target_pecha.layers.items():
        for _, value_ in target_segment_yml.items():
            target_annotations = value_.annotations

    
    source_span = get_span(source_annotations)
    target_span = get_span(target_annotations)
 
    expected_source_segment = load_yaml(
        Path("./tests/data/alignment/tmx/expected_source_segment.yml")
    )
    expected_target_segment = load_yaml(
        Path("./tests/data/alignment/tmx/expected_target_segment.yml")
    )
    expected_source_span = get_span(expected_source_segment['annotations'], "expected")
    expected_target_span = get_span(expected_target_segment['annotations'], "expected")

    assert source_span == expected_source_span
    assert target_span == expected_target_span

if __name__ =="__main__":
    test_create_tmx_to_opf()