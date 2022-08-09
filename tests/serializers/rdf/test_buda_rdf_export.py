from pathlib import Path
import rdflib

from openpecha.serializers import BUDARDFSerializer
from openpecha.core.pecha import OpenPechaFS


def test_buda_rdf_serializer():
    opf_path = Path(__file__).parent / "I0123" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123" / "I0123-expected.ttl"
    op = OpenPechaFS("I0123", opf_path)
    serializer = BUDARDFSerializer(op)
    serializer.apply_layers()
    results = serializer.get_result()
    print(results.serialize(format="ttl").decode("utf-8"))
    expected = rdflib.Graph().parse(str(expected_path))
    assert results == expected

if __name__ == "__main__":
    test_buda_rdf_serializer()