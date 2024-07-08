from pathlib import Path
import rdflib
from rdflib.compare import graph_diff, to_isomorphic
import json
from jsondiff import diff

from openpecha.serializers import BUDAElasticSearchSerializer
from openpecha.core.pecha import OpenPechaFS

def remove_dateTimes(g):
    for s, p, o in g.triples((None, rdflib.URIRef("http://purl.bdrc.io/ontology/core/OPFOCRTimeStamp"), None)):
        g.remove((s, p, o))

def test_buda_es_serializer():
    opf_path = Path(__file__).parent / "I0123" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123" / "I0123-expected.json"

    op = OpenPechaFS(opf_path, "I0123")
    serializer = BUDAElasticSearchSerializer(op)
    serializer.apply_layers()
    docs = serializer.get_result()
    print(json.dumps(docs, ensure_ascii=False))
    expected = None
    with open(expected_path) as f:
        expected = json.load(f)
    difference = diff(expected, docs)
    if difference:
        print("results differ from expectations, diff is:")
        print(difference)
        assert False
    assert True

if __name__ == "__main__":
    test_buda_es_serializer()