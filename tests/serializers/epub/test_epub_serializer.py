import tempfile
from pathlib import Path

from openpecha.serializers import EpubSerializer
from openpecha.utils import load_yaml


def test_opf_2_tsadra_serializer():
    opf_path = Path(__file__).parent / "data" / "P000801" / "P000801.opf"
    with tempfile.TemporaryDirectory() as tmpdirname:
        serializer = EpubSerializer(opf_path)
        out_fn = serializer.serialize(output_path=tmpdirname)
        assert out_fn.name == "P000801.epub"


def test_opf_2_html_serializer():
    opf_path = Path(__file__).parent / "data" / "P000801" / "P000801.opf"
    expected_serialized_html = (
        Path(__file__).parent / "data" / "serialized_P000801.html"
    ).read_text(encoding="utf-8")
    serializer = EpubSerializer(opf_path)
    pecha_title = serializer.meta["source_metadata"].get("title", "")
    serializer.apply_layers()

    results = serializer.get_result()
    for vol_id, result in results.items():
        serialized_html = serializer.get_serialized_html(result, vol_id, pecha_title)
        assert expected_serialized_html == serialized_html
