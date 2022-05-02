from turtle import up

from docs_src.developer.layer import (
    add_annotation,
    bump_revision,
    create_layer,
    get_annotation,
    update_annotation,
)


def test_create_layer():
    create_layer.layer


def test_add_annotation():
    add_annotation.layer


def test_get_annotation():
    get_annotation.layer


def test_bump_revision():
    bump_revision.layer


def test_update_annotation():
    assert update_annotation.new_ann.span.start == 15
