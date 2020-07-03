from uuid import uuid4

from openpecha.formatters.layers import *
from openpecha.formatters.layers import AnnType, Span, _attr_names


def test_span():
    start, end = 100, 200
    span = Span(start, end)

    result = span

    expected = {_attr_names.START: start, _attr_names.END: end}
    assert expected == result


def get_fake_pg():
    return 100, 200, "1a", "first page", "1000.png"


def test_ann():
    start, end, pg_index, pg_info, pg_ref = get_fake_pg()
    span = Span(start, end)
    page = Page(span, page_index=pg_index, page_info=pg_info, page_ref=pg_ref)

    result = page

    expected = {
        _attr_names.PAGE_INDEX: pg_index,
        _attr_names.PAGE_INFO: pg_info,
        _attr_names.PAGE_REFERENCE: pg_ref,
        _attr_names.SPAN: {_attr_names.START: start, _attr_names.END: end},
    }

    assert expected == result


def test_layer():
    # create Page layer
    layer_id = uuid4().hex
    ann_type = AnnType.pagination
    rev = f"{1:05}"
    Pagination_layer = Layer(layer_id, ann_type, rev=rev)
    start, end, pg_index, pg_info, pg_ref = get_fake_pg()

    # create page annotaion
    span = Span(start, end)
    page = Page(span, page_index=pg_index, page_info=pg_info, page_ref=pg_ref)
    pg_id = uuid4().hex
    Pagination_layer[_attr_names.ANNOTATION][pg_id] = page

    result = Pagination_layer

    expected = {
        _attr_names.ID: layer_id,
        _attr_names.ANNOTATION_TYPE: ann_type,
        _attr_names.REVISION: rev,
        _attr_names.ANNOTATION: {
            pg_id: {
                _attr_names.PAGE_INDEX: pg_index,
                _attr_names.PAGE_INFO: pg_info,
                _attr_names.PAGE_REFERENCE: pg_ref,
                _attr_names.SPAN: {_attr_names.START: start, _attr_names.END: end},
            }
        },
    }

    assert expected == result
