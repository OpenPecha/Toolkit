import tempfile
from pathlib import Path

from openpecha.serializers.elan import ElanSerializer


input_opf_path = Path(__file__).parent / "data" / "I99A9986A" / "I99A9986A.opf"
expected_elan = (Path(__file__).parent / "data" / "expected_elan.eaf").read_text(
    encoding="utf8"
)


def test_elan_serialize():
    elan_serializer = ElanSerializer(input_opf_path)
    for base_id, elan in elan_serializer.serialize():
        assert elan == expected_elan


if __name__ == "__main__":
    test_elan_serialize()
