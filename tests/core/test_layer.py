import pytest
from pydantic import ValidationError

from openpecha.core.annotations import Citation, Span
from openpecha.core.layer import Layer, LayerEnum


def test_layer_model():
    layer = Layer(
        annotation_type=LayerEnum.book_title, revision="00001", annotations={}
    )
    assert layer.annotation_type.value == "BookTitle"
    assert layer.revision == "00001"
    layer.bump_revision()
    assert layer.revision == "00002"


def test_not_supported_layer():
    with pytest.raises(ValidationError):
        Layer(annotation_type="NotSupportedLayer", revision="00001", annotations={})


def test_revision_should_be_int_parsible():
    with pytest.raises(ValidationError):
        Layer(annotation_type=LayerEnum.book_title, revision="1aaa", annotations={})


def test_layer_reset():
    layer = Layer(
        annotation_type=LayerEnum.book_title, revision="00003", annotations={"1": "ann"}
    )
    assert layer.revision == "00003"
    assert layer.annotations
    layer.reset()
    assert layer.revision == "00001"
    assert layer.annotations == {}


def test_add_annotation():
    layer = Layer(annotation_type=LayerEnum.citation)
    ann = Citation(span=Span(start=10, end=20))

    layer.set_annotation(ann)

    assert layer.annotations[ann.id]["id"] == ann.id


def test_get_annotation():
    layer = Layer(annotation_type=LayerEnum.citation)
    ann = Citation(span=Span(start=10, end=20))

    layer.set_annotation(ann)

    assert layer.get_annotation(ann.id).id == ann.id


def test_remove_annotation():
    layer = Layer(annotation_type=LayerEnum.citation)
    ann = Citation(span=Span(start=10, end=20))

    layer.set_annotation(ann)

    assert ann.id in layer.annotations

    layer.remove_annotation(ann.id)

    assert ann.id not in layer.annotations
