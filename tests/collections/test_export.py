from openpecha.collection import Collection
from openpecha import config


def test_export():
    obj = Collection("chojuk")
    zip_path = obj.export("plain")
    path = f"{config.COLLECTIONS_PATH}/chojuk.zip"
    assert zip_path == path
