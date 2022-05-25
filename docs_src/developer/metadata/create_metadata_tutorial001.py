from openpecha.core.metadata import InitialCreationType, InitialPechaMetadata

metadata = InitialPechaMetadata(
    source="https://library.bdrc.io",
    source_file="https://library.bdrc.io/text.json",
    initial_creation_type=InitialCreationType.ocr,
    parser="https://github.com/OpenPecha-dev/openpecha-toolkit/pgoogle_orc.py",
    source_metadata={
        "id": "bdr:W1PD90121",
        "title": "མའོ་རྫོང་གི་ས་ཆའི་མིང་བཏུས།",
        "author": "author name",
    },
)


assert metadata.id.startswith("I")
