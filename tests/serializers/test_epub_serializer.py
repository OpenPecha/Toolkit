import tempfile
from pathlib import Path

from openpecha.serializers import EpubSerializer
from openpecha.utils import load_yaml


def test_opf_2_tsadra_serializer():
    opf_path = Path("./tests/data/serialize/tsadra/P000801/P000801.opf")
    with tempfile.TemporaryDirectory() as tmpdirname:
        serializer = EpubSerializer(opf_path)
        out_fn = serializer.serialize(output_path=tmpdirname)
        assert out_fn.name == "P000801.epub"


def test_opf_2_html_serializer():
    opf_path = Path("./tests/data/serialize/tsadra/P000801/P000801.opf")
    expected_serialized_html = Path('./tests/data/serialize/tsadra/serialized_P000801.html').read_text(encoding='utf-8')
    serializer = EpubSerializer(opf_path)
    pecha_title = serializer.meta["source_metadata"].get("title", "")
    serializer.apply_layers()

    results = serializer.get_result()
    for vol_id, result in results.items():
        result = f"{serializer.get_front_page()}{result}"
        footnote_ref_tag = ""
        if "Footnote" in serializer.layers:
            footnote_fn = serializer.opf_path / "layers" / vol_id / "Footnote.yml"
            footnote_layer = load_yaml(footnote_fn)
            footnote_ref_tag = serializer.get_footnote_references(
                footnote_layer["annotations"]
            )
        result = serializer.p_tag_adder(result)
        result = serializer.indentation_adjustment(result)
        serialized_html = (
            f"<html>\n<head>\n\t<title>{pecha_title}</title>\n</head>\n<body>\n"
        )
        serialized_html += f"{result}{footnote_ref_tag}</body>\n</html>"
        assert expected_serialized_html == serialized_html
