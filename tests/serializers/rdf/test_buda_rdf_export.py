from pathlib import Path
import rdflib
from rdflib.compare import graph_diff

from openpecha.serializers import BUDARDFSerializer
from openpecha.core.pecha import OpenPechaFS


def test_buda_rdf_serializer():
    opf_path = Path(__file__).parent / "I0123" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123" / "I0123-expected.ttl"
    op = OpenPechaFS("I0123", opf_path)
    serializer = BUDARDFSerializer(op)
    serializer.apply_layers()
    results = serializer.get_result()
    #print(results.serialize(format="ttl"))
    expected = rdflib.Graph().parse(str(expected_path), format="ttl")
    print(graph_diff(results, expected)[1].serialize(format="ttl"))
    assert results == expected

if __name__ == "__main__":
    test_buda_rdf_serializer()