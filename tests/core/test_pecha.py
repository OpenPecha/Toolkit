import tempfile

import pytest

from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, MetaData
from openpecha.core.pecha import OpenPechaFS


@pytest.fixture(scope="module")
def pecha():
    return OpenPechaFS("tests/data/pechas/P000100.opf")


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


def test_load_openpecha(pecha):
    assert pecha.meta.id
    assert pecha.index
    assert pecha.get_base("v001")
    assert pecha.get_layer("v001", LayerEnum.citation)
    assert pecha.components

    with tempfile.TemporaryDirectory() as tmpdirname:
        pecha.save(tmpdirname)


def test_save_layer(pecha):
    pecha.save_layer(
        "v002",
        LayerEnum.citation,
        Layer(
            annotation_type=LayerEnum.citation,
            revision="00001",
            annotations={},
        ),
    )


def test_pecha_update(pecha):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pecha.meta.id
        pecha.get_base("v001")
        pecha.get_layer("v001", LayerEnum.citation)
        pecha.save(tmpdirname)

        pecha.update_base("v001", "update base")
        pecha.update_layer(
            "v001",
            LayerEnum.citation,
            Layer(
                annotation_type=LayerEnum.citation,
                revision="00001",
                annotations={"1": "update annotation"},
            ),
        )

        pecha.reset_base_and_layers()
        assert pecha.get_base("v001") == "update base"
        assert (
            pecha.get_layer("v001", LayerEnum.citation).annotations["1"]
            == "update annotation"
        )


def test_create_empty_layer(pecha):
    layer = pecha.get_layer("v001", LayerEnum("BookNumber"))
    assert layer.annotation_type == LayerEnum("BookNumber")
    assert layer.revision == "00001"
    assert layer.annotations == {}
