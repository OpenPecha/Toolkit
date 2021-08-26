from pathlib import Path

from openpecha.serializers.docx import DocxSerializer

def test_serialize_docx():
    opf_path = Path("./tests/data/serialize/docx/P1.opf")
    docx_serializer = DocxSerializer(opf_path)
    output_path = Path("./tests/data/serialize/docx")
    assert output_path == docx_serializer.serialize(output_path)
    # (output_path / "P1.docx").unlink()