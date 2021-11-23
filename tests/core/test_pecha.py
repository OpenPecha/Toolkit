import shutil
import tempfile

import pytest

from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS


@pytest.fixture(scope="module")
def opf_path():
    return "tests/data/pechas/P000100.opf"


def test_create_pecha():
    openpecha = OpenPechaFS(
        base={"v001": "this is base"},
        layers={
            "v001": {
                LayerEnum.citation: Layer(
                    annotation_type=LayerEnum.citation, revision="00001", annotations={}
                )
            }
        },
        meta=PechaMetaData(initial_creation_type=InitialCreationEnum.ebook),
    )
    assert openpecha.meta.id
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayerEnum.citation)

    with tempfile.TemporaryDirectory() as tmpdirname:
        assert openpecha.save(tmpdirname)


def test_load_openpecha(opf_path):
    pecha = OpenPechaFS(opf_path)
    assert pecha.meta.id
    assert pecha.index
    assert pecha.get_base("v001")
    assert pecha.get_layer("v001", LayerEnum.citation)
    assert pecha.components

    with tempfile.TemporaryDirectory() as tmpdirname:
        pecha.save(tmpdirname)


def test_save_layer(opf_path):
    pecha = OpenPechaFS(opf_path)
    layer_fn = pecha.save_layer(
        "v002",
        LayerEnum.citation,
        Layer(annotation_type=LayerEnum.citation, revision="00001", annotations={}),
    )
    assert layer_fn.is_file()
    shutil.rmtree(str(layer_fn.parent))


def test_pecha_update(opf_path):
    pecha = OpenPechaFS(opf_path)
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


def test_create_empty_layer(opf_path):
    pecha = OpenPechaFS(opf_path)
    layer = pecha.get_layer("v001", LayerEnum("BookNumber"))
    assert layer.annotation_type == LayerEnum("BookNumber")
    assert layer.revision == "00001"
    assert layer.annotations == {}


def test_reset_layer(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_name, layer_name = "v001", LayerEnum.citation
    with tempfile.TemporaryDirectory() as tmpdirname:
        pecha.meta.id
        pecha.get_base(base_name)
        pecha.get_layer(base_name, layer_name)
        pecha.save(tmpdirname)

        pecha.reset_layer(base_name, layer_name)
        assert not pecha.layers[base_name][layer_name]
        pecha.get_layer(base_name, layer_name)
        assert not pecha.layers[base_name][layer_name].annotations


def test_reset_layers(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_name, layer_name_1, layer_name_2 = "v001", LayerEnum.citation, LayerEnum.author
    with tempfile.TemporaryDirectory() as tmpdirname:
        pecha.meta.id
        pecha.get_base(base_name)
        pecha.get_base(base_name)
        pecha.get_layer(base_name, layer_name_1)
        pecha.get_layer(base_name, layer_name_2)
        pecha.save(tmpdirname)

        pecha.reset_layers(base_name, exclude=[layer_name_2])
        assert not pecha.layers[base_name][layer_name_1]
        assert pecha.layers[base_name][layer_name_2]
        pecha.get_layer(base_name, layer_name_1)
        pecha.get_layer(base_name, layer_name_2)
        assert not pecha.layers[base_name][layer_name_1].annotations
        assert pecha.layers[base_name][layer_name_2].annotations
