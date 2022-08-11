from openpecha.buda.api import _res_from_model
from pathlib import Path
import rdflib
import json

def test_buda_info_from_model():
    ttl_path = Path(__file__).parent / "data" / "OP_info-W12827.ttl"
    g = rdflib.Graph().parse(str(ttl_path), format="ttl")
    res = _res_from_model(g, "W12827")
    expected_path = Path(__file__).parent / "data" / "expected-W12827.json"
    with open(expected_path) as expected_file:
        expected = json.load(expected_file)
        assert res == expected

if __name__ == "__main__":
    test_buda_info_from_model()