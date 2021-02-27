import pytest
from pydantic import ValidationError

from openpecha.core.layer import Layer, LayerEnum


def test_layer_model():
    layer = Layer(
        annotation_type=LayerEnum.book_title, revision="00001", annotations={}
    )
    assert layer.annotation_type.value == "BookTitle"
    assert layer.revision == "00001"


def test_not_supported_layer():
    with pytest.raises(ValidationError):
        Layer(annotation_type="NotSupportedLayer", revision="00001", annotations={})


def test_revision_should_be_int_parsible():
    with pytest.raises(ValidationError):
        Layer(annotation_type=LayerEnum.book_title, revision="1aaa", annotations={})
