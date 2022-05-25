from datetime import datetime

from openpecha.core import ids
from openpecha.core.metadata import (
    Copyright,
    CopyrightStatus,
    DiplomaticPechaMetadata,
    InitialCreationType,
    InitialPechaMetadata,
    LicenseType,
    OpenPechaMetadata,
    PechaMetadata,
)


def test_base_pecha_metadata_model():
    imported_at = datetime.fromisoformat("2020-01-01T00:00:00")
    last_modified_at = datetime.fromisoformat("2020-01-01T00:00:00")

    metadata = PechaMetadata(
        id=ids.get_initial_pecha_id(),
        source="https://library.bdrc.io",
        source_file="https://library.bdrc.io/text.json",
        initial_creation_type=InitialCreationType.ocr,
        imported=imported_at,
        last_modified=last_modified_at,
        parser="https://github.com/OpenPecha-dev/openpecha-toolkit/pgoogle_orc.py",
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
    assert metadata.initial_creation_type.value == InitialCreationType.ocr.value
    assert metadata.id.startswith("I")
    assert len(metadata.id) == 9


def test_initial_pecha_metadata():
    metadata = InitialPechaMetadata(
        initial_creation_type=InitialCreationType.ocr,
    )

    assert metadata.initial_creation_type.value == InitialCreationType.ocr.value
    assert metadata.id.startswith("I")


def test_diplomatic_pecha_metadata():
    metadata = DiplomaticPechaMetadata(
        initial_creation_type=InitialCreationType.ocr,
    )

    assert metadata.initial_creation_type.value == InitialCreationType.ocr.value
    assert metadata.id.startswith("D")


def test_open_pecha_metadata():
    metadata = OpenPechaMetadata(
        initial_creation_type=InitialCreationType.ocr,
    )

    assert metadata.initial_creation_type.value == InitialCreationType.ocr.value
    assert metadata.id.startswith("O")


def test_pecha_copyright():
    copyright_status = CopyrightStatus.COPYRIGHTED

    copyright = Copyright(
        status=copyright_status,
        notice="Copyright 2022 OpenPecha",
        info_url="https://dev.openpecha.org",
    )

    metadata = InitialPechaMetadata(
        initial_creation_type=InitialCreationType.ocr, copyright=copyright
    )

    assert metadata.copyright.status == copyright_status


def test_pecha_licence():
    license_type = LicenseType.CC_BY_NC_SA

    metadata = InitialPechaMetadata(
        initial_creation_type=InitialCreationType.ocr, license=license_type
    )

    assert metadata.license == license_type
