from pathlib import Path

import pytest

from openpecha.core.layer import LayerEnum
from openpecha.formatters.editor import EditorParser
from openpecha.serializers.epub import TsadraTemplateCSSClasses


@pytest.fixture(scope="module")
def editor_content():
    return Path("tests/data/formatter/editor/editor_output.html").read_text()


def test_parser_editor_content_no_grouping(editor_content):
    parser = EditorParser()
    parser.parse("v001", editor_content, group_verse=False)
    print(parser.base)
    print(parser.layers)

    for layer_name, layer in parser.layers["v001"].items():
        for ann_id, ann in layer.annotations.items():
            assert (
                parser.base["v001"][ann.span.start : ann.span.end + 1]
                == f"{layer_name.value} {ann_id}"
            )


def assert_ann(parser, base_name, layer_name, ann_id, excepted, metadata={}):
    layer = parser.layers[base_name][LayerEnum(layer_name)]
    ann = layer.annotations[ann_id]
    assert parser.base[base_name][ann.span.start : ann.span.end + 1] == excepted
    assert ann.metadata == metadata


def test_parser_editor_content_with_grouping(editor_content):
    parser = EditorParser()
    parser.parse("v001", editor_content, group_verse=True)

    assert_ann(
        parser,
        base_name="v001",
        layer_name="Tsawa",
        ann_id="1",
        excepted="Tsawa 1\nTsawa 2",
        metadata={"css_class_name": TsadraTemplateCSSClasses.tsawa_verse.value},
    )
    assert_ann(
        parser,
        base_name="v001",
        layer_name="Tsawa",
        ann_id="3",
        excepted="Tsawa 3",
        metadata={"css_class_name": TsadraTemplateCSSClasses.tsawa_inline.value},
    )
    assert_ann(
        parser,
        base_name="v001",
        layer_name="Tsawa",
        ann_id="4",
        excepted="Tsawa 4\nTsawa 5",
        metadata={"css_class_name": TsadraTemplateCSSClasses.tsawa_verse.value},
    )

    assert_ann(
        parser,
        base_name="v001",
        layer_name="Citation",
        ann_id="1",
        excepted="Citation 1",
        metadata={"css_class_name": TsadraTemplateCSSClasses.citation_inline.value},
    )
    assert_ann(
        parser,
        base_name="v001",
        layer_name="Citation",
        ann_id="2",
        excepted="Citation 2\nCitation 3",
        metadata={"css_class_name": TsadraTemplateCSSClasses.citation_verse.value},
    )
    assert_ann(
        parser,
        base_name="v001",
        layer_name="Citation",
        ann_id="4",
        excepted="Citation 4",
        metadata={"css_class_name": TsadraTemplateCSSClasses.citation_inline.value},
    )
    assert_ann(
        parser,
        base_name="v001",
        layer_name="Citation",
        ann_id="5",
        excepted="Citation 5",
        metadata={"css_class_name": TsadraTemplateCSSClasses.citation_prose.value},
    )
