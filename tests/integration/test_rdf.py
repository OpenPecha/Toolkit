import os
from pathlib import Path
import rdflib

from openpecha.serializers import Rdf
from openpecha.buda.op_fs import OpenpechaFS

if __name__ == "__main__":
    op = OpenpechaFS("P0RDF001", "./tests/data/serialize/rdf/P0RDF001.opf")
    ser = Rdf("P0RDF001", op)
    graph = ser.get_graph()
    expected = rdflib.Graph()
    expected.parse("./tests/data/serialize/rdf/expected.ttl", format="turtle")
    if graph.isomorphic(expected):
        print("serialization works as expected")
    else:
        print("serialization doesn't work as expected. Expected the content of tests/data/serialize/rdf/expected.ttl but instead got:")
        print(graph.serialize(format="turtle").decode("utf-8"))