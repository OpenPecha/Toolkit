from pathlib import Path

import pytest

from openpecha.core.layer import LayerEnum
from openpecha.formatters.editor import EditorParser


@pytest.fixture(scope="module")
def editor_content():
    return Path("tests/data/formatter/editor/editor_output.html").read_text()


def test_parser_editor_content_no_grouping(editor_content):
    parser = EditorParser()
    parser.parse("v001", editor_content, group=False)
    print(parser.base)
    print(parser.layers)

    for layer_name, layer in parser.layers["v001"].items():
        for ann_id, ann in layer.annotations.items():
            assert (
                parser.base["v001"][ann.span.start : ann.span.end + 1]
                == f"{layer_name.value} {ann_id}"
            )


def assert_ann(parser, base_name, layer_name, id_, excepted, is_verse):
    layer = parser.layers[base_name][LayerEnum(layer_name)]
    ann = layer.annotations[id_]
    assert parser.base[base_name][ann.span.start : ann.span.end + 1] == excepted
    assert ann.is_verse == is_verse


def test_parser_editor_content_with_grouping(editor_content):
    parser = EditorParser()
    parser.parse("v001", editor_content, group=True)

    assert_ann(parser, "v001", "Tsawa", "1", "Tsawa 1\nTsawa 2", True)
    assert_ann(parser, "v001", "Tsawa", "3", "Tsawa 3", False)
    assert_ann(parser, "v001", "Tsawa", "4", "Tsawa 4\nTsawa 5", True)

    assert_ann(parser, "v001", "Citation", "1", "Citation 1", False)
    assert_ann(parser, "v001", "Citation", "2", "Citation 2\nCitation 3", True)
    assert_ann(parser, "v001", "Citation", "4", "Citation 4", False)
