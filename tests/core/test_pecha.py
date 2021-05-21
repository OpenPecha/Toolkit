import tempfile

from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, MetaData
from openpecha.core.pecha import OpenPechaFS


def test_create_pecha():
    openpecha = OpenPechaFS(
        base={"v001": "this is base"},
        layers={
            "v001": {
                LayerEnum.citation: Layer(
                    annotation_type=LayerEnum.citation,
                    revision="00001",
                    annotations={},
                )
            }
        },
        meta=MetaData(initial_creation_type=InitialCreationEnum.ebook),
    )
    assert openpecha.meta.id
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayerEnum.citation)

    with tempfile.TemporaryDirectory() as tmpdirname:
        assert openpecha.save(tmpdirname)


def test_load_openpecha():
    openpecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")
    assert openpecha.meta.id
    assert openpecha.index
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayerEnum.citation)
    assert openpecha.components

    with tempfile.TemporaryDirectory() as tmpdirname:
        openpecha.save(tmpdirname)


def test_save_layer():
    openpecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")
    openpecha.save_layer(
        "v002",
        LayerEnum.citation,
        Layer(
            annotation_type=LayerEnum.citation,
            revision="00001",
            annotations={},
        ),
    )


def test_pecha_update():
    openpecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")

    with tempfile.TemporaryDirectory() as tmpdirname:
        openpecha.meta.id
        openpecha.get_base("v001")
        openpecha.get_layer("v001", LayerEnum.citation)
        openpecha.save(tmpdirname)

        openpecha.update_base("v001", "update base")
        openpecha.update_layer(
            "v001",
            LayerEnum.citation,
            Layer(
                annotation_type=LayerEnum.citation,
                revision="00001",
                annotations={"1": "update annotation"},
            ),
        )

        openpecha.reset_base_and_layers()
        assert openpecha.get_base("v001") == "update base"
        assert (
            openpecha.get_layer("v001", LayerEnum.citation).annotations["1"]
            == "update annotation"
        )


def test_create_empty_layer():
    pecha = OpenPechaFS("tests/data/serialize/tsadra/P000100.opf")
    layer = pecha.get_layer("v001", LayerEnum("BookNumber"))
    assert layer.annotation_type == LayerEnum("BookNumber")
    assert layer.revision == "00001"
    assert layer.annotations == {}
