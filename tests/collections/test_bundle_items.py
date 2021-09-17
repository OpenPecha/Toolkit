from openpecha.collection import Collection
from openpecha.config import _mkdir
from pathlib import Path

def test_bundle_items():
    items = ["W00000003","P000121", "P000131"]
    ob = Collection(None)
    ob.bundle_items(items)