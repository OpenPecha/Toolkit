from pathlib import Path


from openpecha.serializers import EditorSerializer


def test_editor_serializer():
    opf_path = "./tests/data/serialize/tsadra/P000801/P000801.opf"
    expected_output = Path(
        "./tests/data/serialize/tsadra/editor_serializer_output.html"
    ).read_text(encoding="utf-8")
    serializer = EditorSerializer(opf_path)
    for base_name, result in serializer.serialize():
        assert base_name
        assert result == expected_output