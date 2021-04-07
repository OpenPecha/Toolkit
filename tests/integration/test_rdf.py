import os
from pathlib import Path

from openpecha.serializers import Rdf
from openpecha.buda.op_fs import OpenpechaFS

if __name__ == "__main__":
    op = OpenpechaFS("P0RDF001", "./tests/data/serialize/rdf/P0RDF001.opf")
    ser = Rdf("P0RDF001", op)
    graph = ser.get_graph()
    print(graph.serialize(format="turtle").decode("utf-8"))