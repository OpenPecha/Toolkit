from openpecha.collection import Collection
from openpecha import config


def test_export():
    obj = Collection("chojuk")
    export_path = obj.export("plain")
    assert export_path == f"{config.COLLECTIONS_PATH}/chojuk"
