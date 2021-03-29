import tempfile

from openpecha.core.layer import InitialCreationEnum, Layer, LayersEnum, MetaData
from openpecha.core.pecha import OpenPechaFS


def test_create_pecha():
    openpecha = OpenPechaFS(
        base={"v001": "this is base"},
        layers={
            "v001": {
                LayersEnum.citation: Layer(
                    annotation_type=LayersEnum.citation,
                    revision="00001",
                    annotations={},
                )
            }
        },
        meta=MetaData(id="P000001", initial_creation_type=InitialCreationEnum.ebook),
    )
    assert openpecha.meta.id
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayersEnum.citation)


def test_load_openpecha():
    openpecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")
    assert openpecha.meta.id
    assert openpecha.index
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayersEnum.citation)
    assert openpecha.components

    with tempfile.TemporaryDirectory() as tmpdirname:
        openpecha.save(tmpdirname)


def test_save_layer():
    openpecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")
    openpecha.save_layer(
        "v002",
        LayersEnum.citation,
        Layer(
            annotation_type=LayersEnum.citation,
            revision="00001",
            annotations={},
        ),
    )


def test_pecha_update():
    openpecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")

    with tempfile.TemporaryDirectory() as tmpdirname:
        openpecha.meta.id
        openpecha.get_base("v001")
        openpecha.get_layer("v001", LayersEnum.citation)
        openpecha.save(tmpdirname)

        openpecha.update_base("v001", "update base")
        openpecha.update_layer(
            "v001",
            LayersEnum.citation,
            Layer(
                annotation_type=LayersEnum.citation,
                revision="00001",
                annotations={"1": "update annotation"},
            ),
        )

        openpecha.reset_base_and_layers()
        assert openpecha.get_base("v001") == "update base"
        assert (
            openpecha.get_layer("v001", LayersEnum.citation).annotations["1"]
            == "update annotation"
        )


def test_create_empty_layer():
    pecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")
    layer = pecha.get_layer("v001", LayersEnum("BookNumber"))
    assert layer.annotation_type == LayersEnum("BookNumber")
    assert layer.revision == "00001"
    assert layer.annotations == {}
