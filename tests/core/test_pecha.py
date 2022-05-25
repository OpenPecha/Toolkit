import shutil
import tempfile
from pathlib import Path

import pytest

from openpecha.core.annotations import Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.metadata import InitialCreationType, InitialPechaMetadata
from openpecha.core.pecha import OpenPecha, OpenPechaFS


@pytest.fixture(scope="module")
def opf_path():
    return "tests/data/pechas/P000100.opf"


@pytest.fixture(scope="module")
def test_pechas_path():
    return Path("tests/data/pechas")


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
        metadata=InitialPechaMetadata(initial_creation_type=InitialCreationType.ebook),
    )
    assert openpecha.meta.id
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayerEnum.citation)

    with tempfile.TemporaryDirectory() as tmpdirname:
        assert openpecha.save(tmpdirname)


def test_load_openpecha(opf_path):
    pecha = OpenPechaFS(path=opf_path)
    assert pecha.meta.id
    assert pecha.index
    assert pecha.get_base("v001")
    assert pecha.get_layer("v001", LayerEnum.citation)
    assert pecha.components

    with tempfile.TemporaryDirectory() as tmpdirname:
        pecha.save(tmpdirname)


def test_save_layer(opf_path):
    pecha = OpenPechaFS(path=opf_path)
    layer_fn = pecha.save_layer(
        "v002",
        LayerEnum.citation,
        Layer(annotation_type=LayerEnum.citation, revision="00001", annotations={}),
    )
    assert layer_fn.is_file()
    shutil.rmtree(str(layer_fn.parent))


def test_pecha_update(opf_path):
    pecha = OpenPechaFS(path=opf_path)
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
    pecha = OpenPechaFS(path=opf_path)
    layer = pecha.get_layer("v001", LayerEnum("BookNumber"))
    assert layer.annotation_type == LayerEnum("BookNumber")
    assert layer.revision == "00001"
    assert layer.annotations == {}


def test_reset_layer(opf_path):
    pecha = OpenPechaFS(path=opf_path)
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
    pecha = OpenPechaFS(path=opf_path)
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


def test_set_base():
    metadata = InitialPechaMetadata(initial_creation_type=InitialCreationType.input)
    pecha = OpenPecha(metadata=metadata)

    base_name = pecha.set_base("base content")

    assert pecha.base[base_name] == "base content"


def test_set_base_metadata():
    metadata = InitialPechaMetadata(initial_creation_type=InitialCreationType.input)
    pecha = OpenPecha(metadata=metadata)
    base_metadata = {"id": "id", "title": "title"}

    base_name = pecha.set_base("base content", metadata=base_metadata)

    assert base_name in pecha.meta.source_metadata["base"]
    assert pecha.meta.source_metadata["base"][base_name]["id"] == "id"
    assert pecha.meta.source_metadata["base"][base_name]["title"] == "title"
    assert (
        pecha.meta.source_metadata["base"][base_name]["base_file"] == f"{base_name}.txt"
    )


def test_set_layer():
    metadata = InitialPechaMetadata(initial_creation_type=InitialCreationType.input)
    pecha = OpenPecha(metadata=metadata)
    base_name = pecha.set_base("base content")
    layer = Layer(annotation_type=LayerEnum.citation)

    pecha.set_layer(base_name, layer)

    assert pecha.layers[base_name][LayerEnum.citation].id == layer.id


def get_sub_string(string, span):
    return string[span.start : span.end + 1]  # noqa E203


def test_span_info_with_layers(test_pechas_path):
    opf_path = test_pechas_path / "span_info.opf"
    pecha = OpenPechaFS(path=opf_path)

    span_info = pecha.get_span_info(
        base_name="0001",
        span=Span(start=16, end=33),
        layers=[LayerEnum.citation, LayerEnum.tsawa, LayerEnum.yigchung],
    )

    assert (
        get_sub_string(span_info.text, span_info.layers[LayerEnum.citation][0].span)
        == "cc"
    )

    assert (
        get_sub_string(span_info.text, span_info.layers[LayerEnum.tsawa][0].span)
        == "rrrr\nrrrr"
    )

    assert (
        get_sub_string(span_info.text, span_info.layers[LayerEnum.yigchung][0].span)
        == "yy"
    )


def test_span_info_without_layers(test_pechas_path):
    opf_path = test_pechas_path / "span_info.opf"
    pecha = OpenPechaFS(path=opf_path)

    span_info = pecha.get_span_info(
        base_name="0001",
        span=Span(start=1, end=10),
        layers=[LayerEnum.citation, LayerEnum.tsawa, LayerEnum.yigchung],
    )

    assert not span_info.layers


@pytest.mark.skip(reason="external api call")
def test_download_pecha():
    pecha = OpenPechaFS(pecha_id="P000108")

    assert pecha.opf_path.is_dir()

    shutil.rmtree(str(pecha.opf_path.parent))

    assert not pecha.opf_path.is_dir()
