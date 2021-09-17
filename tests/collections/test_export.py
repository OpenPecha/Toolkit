from openpecha.collection import Collection


def test_export():
    obj = Collection("cojuk")
    obj.export("plain")
