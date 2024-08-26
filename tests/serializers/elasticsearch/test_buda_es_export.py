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

def get_w_info(w_lname, with_outline = False):
    res = {
            "source_metadata": {
                "reproduction_of": "MW123"
            },
            "image_groups": {
                "I1KG16930": {
                    "volume_number": 1,
                    "volume_pages_bdrc_intro": 2
                }
            }
        }
    if with_outline:
        res["source_metadata"]["outline"] = "O124"
    return res

def get_o_graph(o_lname):
    graph = rdflib.Graph()
    graph.parse(Path(__file__).parent / "I0123-outline" / 'outline.ttl', format='ttl')
    return graph

def test_buda_es_serializer_simple():
    opf_path = Path(__file__).parent / "I0123" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123" / "I0123-expected.json"

    op = OpenPechaFS(opf_path, "I0123")
    serializer = BUDAElasticSearchSerializer(op, get_o_graph=get_o_graph, get_w_info=get_w_info)
    serializer.apply_layers()
    docs = serializer.get_result()
    #print(json.dumps(docs, ensure_ascii=False))
    expected = None
    with open(expected_path) as f:
        expected = json.load(f)
    difference = diff(expected, docs)
    if difference:
        print("results differ from expectations, diff is:")
        print(difference)
        assert False
    assert True

def test_buda_es_serializer_outline():
    opf_path = Path(__file__).parent / "I0123-outline" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123-outline" / "I0123-expected.json"

    op = OpenPechaFS(opf_path, "I0123")
    serializer = BUDAElasticSearchSerializer(op, get_o_graph=get_o_graph, get_w_info=lambda x : get_w_info(x, True))
    serializer.apply_layers()
    docs = serializer.get_result()
    #print(json.dumps(docs, ensure_ascii=False))
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
    test_buda_es_serializer_simple()
    test_buda_es_serializer_outline()