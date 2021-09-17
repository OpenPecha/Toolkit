from openpecha.collection import Collections
import yaml
from pathlib import Path

def test_get_all():
    obj = Collections()
    collections = obj.get_all()
    expected_collection = Path(f"./tests/data/collections/expected_collection.yml").read_text(encoding='utf-8')
    expected_collection = yaml.safe_load(expected_collection)
    assert collections == expected_collection 