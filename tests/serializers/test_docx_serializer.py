from pathlib import Path

from openpecha.serializers.docx import serialize_to_docx

def test_serialize_docx():
    opf_path = Path("./tests/data/serialize/docx/P1.opf")
    output_path = Path("./tests/data/serialize/docx")
    assert output_path == serialize_to_docx(opf_path, output_path)