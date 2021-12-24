import os
import shutil
from pathlib import Path
from openpecha.utils import load_yaml
from openpecha.formatters.dharma_ebooks import create_opf

def clean_dir(layers_output_dir):
    if layers_output_dir.is_dir():
            shutil.rmtree(str(layers_output_dir))


def get_annotation(yml):
    ann = {}
    annotation_name = yml["annotation_name"]
    annotations = yml["annotations"]

    for _, info in annotations.items():
        start = info["span"]["start"]
        end = info["span"]["end"]
        break
    
    ann[annotation_name] = {
            "span":{
                "start": start,
                "end": end
            }
    }
    return ann


def get_annotations(layers_path):
    all_annotations = {}
    tag_types = ["Paragraph_Tag", "Span_Tag"]
    filenames = ["Tibetan-Chapter","Tibetan-Citations-in-Verse_Tibetan-Citations-First-line-alone",
                "Tibetan-Regular-Indented", "Tibetan-Root-Text_Tibetan-Root-Text-First-line-alone",
                "Tibetan-Root-Text_Tibetan-Root-Text-MIddle-Lines", "Tibetan-Root-Text"]

    for filename in filenames:
        for tag_type in tag_types:
            yml_path = Path(layers_path/"RDI-SS-05-9"/f"{tag_type}"/f"{filename}.yml")
            if os.path.isfile(yml_path):
                yml = load_yaml(yml_path)
                ann = get_annotation(yml)
                all_annotations.update(ann)
    return all_annotations


def get_layers_info(opf_path):
    layers_path = Path(opf_path/"layers")
    all_annotations = get_annotations(layers_path)
    return all_annotations


def get_expected_annotations():
    expected_annotations_path = Path("tests") / "formatters" / "dharma_ebooks" / "data" / "expected_annotations.yml"
    expected_annotations = load_yaml(expected_annotations_path)
    return expected_annotations

def assert_number_of_layers(opf_path):
    meta = load_yaml(Path(opf_path/"meta.yml"))
    layers = meta["source_metadata"]["layers"]
    expeected_layers_number = 15
    assert expeected_layers_number == len(layers)
    


def test_dharma_ebooks():
    ebook_path = Path("tests") / "formatters" / "dharma_ebooks" / "data" / "ཐེག་པ་ཆེན་པོའི་གདམས་ངག་བློ་སྦྱོང་དོན་བདུན་མ།"
    output_path = Path("tests") / "formatters" / "dharma_ebooks" / "data" / "pecha"
    opf_path = create_opf(ebook_path, output_path)
    all_annotations = get_layers_info(opf_path)
    expected_annotations = get_expected_annotations()
    result = all_annotations
    expected = expected_annotations
    for (result_ann, result_ann_info), (expected_ann, expected_ann_info) in zip(result.items(), expected.items()):
        assert result_ann == expected_ann
        assert result_ann_info["span"]["start"] == expected_ann_info["span"]["start"]
        assert result_ann_info["span"]["end"] == expected_ann_info["span"]["end"]
    assert_number_of_layers(opf_path)
    clean_dir(output_path)
    