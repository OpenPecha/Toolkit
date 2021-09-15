import tempfile
from pathlib import Path

from openpecha.serializers.docx import DocxSerializer


def test_serialize_docx():
    opf_path = Path("./tests/data/serialize/docx/P1.opf")
    docx_serializer = DocxSerializer(opf_path)
    with tempfile.TemporaryDirectory() as tmpdirname:
        out_fn  = docx_serializer.serialize(output_path=tmpdirname, toc_levels={})
        assert out_fn.name == "P1.docx"

