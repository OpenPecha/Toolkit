from pathlib import Path

from openpecha.serializers import HFMLSerializer


def test_hfml_serializer():
    opf_path = Path(__file__).parent / "data" / "opf" / "P000003.opf/"
    serializer = HFMLSerializer(opf_path)
    serializer.apply_layers()
    hfml_results = serializer.get_result()
    expected_hfml_vol1 = (
        Path(__file__).parent / "data" / "expected_hfml" / "v001.txt"
    ).read_text(encoding="utf-8")
    expected_hfml_vol2 = (
        Path(__file__).parent / "data" / "expected_hfml" / "v002.txt"
    ).read_text(encoding="utf-8")
    assert hfml_results["v001"] == expected_hfml_vol1
    assert hfml_results["v002"] == expected_hfml_vol2
