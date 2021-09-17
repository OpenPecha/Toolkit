from openpecha.collection import Collection

def test_bundle_items():
    items = ["W00000003","P000121", "P000131"]
    ob = Collection(None)
    pecha_ids = ob.bundle_items(items)
    assert pecha_ids != None