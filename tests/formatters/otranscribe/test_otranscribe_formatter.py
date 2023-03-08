from pathlib import Path
from openpecha.formatters import OTranscribeFormatter
from openpecha.core.layer import LayerEnum, Layer
from openpecha.utils import load_yaml_str

input_path = Path(__file__).parent / "data" / "input_otr.otr"
expected_base = (Path(__file__).parent / "data" / "expected_base.txt").read_text(
    encoding="utf8"
)
expected_layer_yml = (
    Path(__file__).parent / "data" / "expected_transcription_time_span_layer.yml"
).read_text(encoding="utf8")
expected_meta_yml = (Path(__file__).parent / "data" / "expected_meta.yml").read_text(
    encoding="utf8"
)


def compare_meta_bases(meta_base_a, meta_base_b):
    def filter_id(pair):
        key, _ = pair
        return key != "id"

    meta_base_a_source_metadata = dict(
        filter(filter_id, meta_base_a["source_metadata"].items())
    )
    meta_base_b_source_metadata = dict(
        filter(filter_id, meta_base_b["source_metadata"].items())
    )

    assert meta_base_a_source_metadata == meta_base_b_source_metadata


def compare_meta(meta_a, meta_b):
    for meta_base_a_key, meta_base_b_key in zip(meta_a["bases"], meta_b["bases"]):
        compare_meta_bases(
            meta_a["bases"][meta_base_a_key], meta_b["bases"][meta_base_b_key]
        )
    assert meta_a["copyright"]["notice"] == meta_b["copyright"]["notice"]
    assert meta_a["copyright"]["status"].value == meta_b["copyright"]["status"]


def compare_annotation(annotation_a, annotation_b):
    assert annotation_a == annotation_b


def compare_layers(layer_a, layer_b):
    assert layer_a.annotation_type == layer_b.annotation_type
    assert layer_a.revision == layer_b.revision
    assert len(layer_a.annotations) == len(layer_b.annotations)

    for annotation_a_key, annotation_b_key in zip(
        layer_a.annotations.keys(), layer_b.annotations.keys()
    ):
        compare_annotation(
            layer_a.annotations[annotation_a_key],
            layer_b.annotations[annotation_b_key],
        )


def test_get_opf():
    formatter = OTranscribeFormatter(media_url="file:///Users/spsither/Desktop/olala.wav")
    output_opf = formatter.create_opf(input_path)

    first_base_name = list(output_opf.meta.bases.keys())[0]

    assert output_opf.get_base(base_name=first_base_name) == expected_base

    output_layer = output_opf.get_layer(
        base_name=first_base_name, layer_name=LayerEnum.transcription_time_span
    )

    expected_layer = Layer.parse_obj(load_yaml_str(expected_layer_yml))
    compare_layers(output_layer, expected_layer)

    compare_meta(output_opf.meta.dict(), load_yaml_str(expected_meta_yml))


if __name__ == "__main__":
    test_get_opf()
