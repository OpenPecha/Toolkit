from pathlib import Path
import rdflib
from rdflib.compare import graph_diff, to_isomorphic

from openpecha.serializers import BUDARDFSerializer
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

def test_buda_rdf_serializer():
    opf_path = Path(__file__).parent / "I0123" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123" / "I0123-expected.ttl"

    op = OpenPechaFS(opf_path, "I0123")
    serializer = BUDARDFSerializer(op, include_contents=False, get_w_info=get_w_info)
    serializer.apply_layers()
    results = serializer.get_result()
    #print(results.serialize(format="ttl"))
    expected = rdflib.Graph().parse(str(expected_path), format="ttl")
    # remove OPFOCRTimeStamp as rdflib believes that 
    #   "1977-04-22T06:00:00+00:00"^^xsd:dateTime and 
    # and
    #   "1977-04-22T06:00:00"^^xsd:dateTime
    # are two different things
    remove_dateTimes(results)
    remove_dateTimes(expected)
    # to look at the differences:
    if to_isomorphic(results) != to_isomorphic(expected):
        print("results differ from expectations, diff is:")
        _, in_results, in_expected = graph_diff(results, expected)
        print("only in results:")
        print(in_results.serialize(format="ttl"))
        print("only in expected:")
        print(in_expected.serialize(format="ttl"))
        assert False
    assert True

def test_buda_rdf_serializer_outline():
    opf_path = Path(__file__).parent / "I0123-outline" / "I0123.opf"
    expected_path = Path(__file__).parent / "I0123-outline" / "I0123-expected.ttl"

    op = OpenPechaFS(opf_path, "I0123")
    serializer = BUDARDFSerializer(op, include_contents=False, get_o_graph=get_o_graph, get_w_info=lambda x : get_w_info(x, True))
    serializer.apply_layers()
    results = serializer.get_result()
    print(results.serialize(format="ttl"))
    expected = rdflib.Graph().parse(str(expected_path), format="ttl")
    # remove OPFOCRTimeStamp as rdflib believes that 
    #   "1977-04-22T06:00:00+00:00"^^xsd:dateTime and 
    # and
    #   "1977-04-22T06:00:00"^^xsd:dateTime
    # are two different things
    remove_dateTimes(results)
    remove_dateTimes(expected)
    # to look at the differences:
    if to_isomorphic(results) != to_isomorphic(expected):
        print("results differ from expectations, diff is:")
        _, in_results, in_expected = graph_diff(results, expected)
        print("only in results:")
        print(in_results.serialize(format="ttl"))
        print("only in expected:")
        print(in_expected.serialize(format="ttl"))
        assert False
    assert True

if __name__ == "__main__":
    test_buda_rdf_serializer()