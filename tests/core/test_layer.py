from datetime import datetime

import pytest
from pydantic import ValidationError

from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData


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


def test_metadata_model():
    created_at = datetime.fromisoformat("2020-01-01T00:00:00")
    last_modified_at = datetime.fromisoformat("2020-01-01T00:00:00")

    metadata = PechaMetaData(
        initial_creation_type=InitialCreationEnum.ocr,
        created_at=created_at,
        last_modified_at=last_modified_at,
    )

    assert metadata.created_at == created_at
    assert metadata.last_modified_at == last_modified_at
    assert metadata.initial_creation_type.value == InitialCreationEnum.ocr.value
    assert metadata.id.startswith("P")
    assert len(metadata.id) == 9
