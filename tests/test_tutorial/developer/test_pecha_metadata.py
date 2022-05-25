from docs_src.developer.metadata import (
    add_copyright_and_license,
    create_metadata_tutorial001,
)


def test_create_metadata():
    assert create_metadata_tutorial001.metadata


def test_add_copyright_and_lincense_tutorial():
    assert add_copyright_and_license.metadata
