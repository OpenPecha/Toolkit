from datetime import datetime

import pytest
from pydantic import ValidationError

from openpecha.core.annotations import Citation, Span
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


def test_metadata_model():
    imported_at = datetime.fromisoformat("2020-01-01T00:00:00")
    last_modified_at = datetime.fromisoformat("2020-01-01T00:00:00")

    metadata = PechaMetaData(
        source="https://library.bdrc.io",
        source_file="https://library.bdrc.io/text.json",
        initial_creation_type=InitialCreationEnum.ocr,
        imported=imported_at,
        last_modified=last_modified_at,
        parser="https://github.com/OpenPecha-dev/openpecha-toolkit/blob/231bba39dd1ba393320de82d4d08a604aabe80fc/openpecha/formatters/google_orc.py",
        source_metadata={
            "id": "bdr:W1PD90121",
            "title": "མའོ་རྫོང་གི་ས་ཆའི་མིང་བཏུས།",
            "author": "author name",
            "base": {
                "f3c9": {
                    "id": "I1PD90137",
                    "title": "Volume 1 of mao wen qiang zu zi zhi xian di ming lu",
                    "total_pages": 220,
                    "order": 1,
                    "base_file": "f3c9.tx",
                }
            },
        },
    )

    assert metadata.imported == imported_at
    assert metadata.last_modified == last_modified_at
    assert metadata.initial_creation_type.value == InitialCreationEnum.ocr.value
    assert metadata.id.startswith("P")
    assert len(metadata.id) == 9
