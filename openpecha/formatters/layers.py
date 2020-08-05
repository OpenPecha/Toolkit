"""This module contains format variable for all the annotations."""

import copy
import re
from collections import namedtuple

__all__ = [
    "Layer",
    "Page",
    "Span",
    "Text",
    "Correction",
    "CrossVolSpan",
    "SubText",
    "Peydurma",
    "OnlySpan",
    "AnnType",
    "create_ann",
]


class AnnType:
    # Layout tags
    pecha_title = "Pecha Title"
    poti_title = "Poti Title"
    chapter_title = "Chapter Title"
    author = "Author"
    yigchung = "Yigchung"
    pagination = "Pagination"
    correction = "Correction"
    error_candidate = "Error Candidate"
    peydurma = "Peydurma"
    tsawa = "Tsawa"
    quotation = "Qoutation"

    not_only_span = [pagination, correction, peydurma]


def create_ann(ann_name, start, end, payloads={}):
    span = Span(start, end)
    if ann_name not in AnnType.not_only_span:
        return OnlySpan(span)
    elif ann_name == AnnType.pagination:
        return Page(span, **payloads)
    elif ann_name == AnnType.correction:
        return Correction(span, **payloads)
    elif ann_name == AnnType.peydurma:
        return Peydurma(span, **payloads)
    else:
        raise NameError(f"{ann_name} annotation not support yet.")


class _attr_names:
    # Layer
    ID = "id"  # Uique id for annotation of specific Pecha or Abstract work. type: str
    ANNOTATION_TYPE = "annotation_type"  # Name of annotation, type: str
    REVISION = "revision"  # Revision number. type: int
    ANNOTATION = "annotations"  # Annotations are stored in list . type: dict

    # Spans
    SPAN = "span"
    START = "start"
    END = "end"

    # Page
    PAGE_INDEX = "page_index"  # Page number based on Volume specified, type: int
    PAGE_INFO = "page_info"  # Page information. type: str
    PAGE_REFERENCE = "reference"  # Any reference of page, eg: img_url. type: str

    # Correction
    CORRECTION = "correction"  # Correct text suggestion. type: str
    CERTAINTY = "certainty"  # Certainty of the suggested correct text. type: int

    # Peydurma
    NOTE = "note"  # syls, word or phrase to be compared to other publication


def Layer(id_, type_, rev=f"{1:05}"):
    return {
        _attr_names.ID: id_,
        _attr_names.ANNOTATION_TYPE: type_,
        _attr_names.REVISION: rev,
        _attr_names.ANNOTATION: {},
    }


def Span(start, end):
    return {_attr_names.START: start, _attr_names.END: end}


# ~~~~~INDEX Layer~~~~~~
# Cross vol Span
CrossVolSpan = {"vol": None, "span": None}

# Sub_text annotation
SubText = {"work": None, "span": []}  # index of the sub_text  # span of the sub_text

# Text annotation
Text = {
    "work": None,  # id of the `text`. type: int
    "parts": [],  # list of SubText
    "span": [],  # list of CrossVolSpan
}


# ~~~~~~ ANNOTATIONS Layers ~~~~~~
def Page(span, *, page_index=None, page_info=None, page_ref=None):
    return {
        _attr_names.PAGE_INDEX: page_index,
        _attr_names.PAGE_INFO: page_info,
        _attr_names.PAGE_REFERENCE: page_ref,
        _attr_names.SPAN: span,
    }


def Correction(span, *, correction=None, certainty=None):
    return {
        _attr_names.CORRECTION: correction,
        _attr_names.CERTAINTY: certainty,
        _attr_names.SPAN: span,
    }


def Peydurma(span, *, note=None):
    return {_attr_names.NOTE: note, _attr_names.SPAN: span}


def OnlySpan(span):
    """Create to create annotation only has a span.

    Annotations inclues:
        - error candidate
        - pecha title
        - poti title
        - author
        - chapter title
        - taswa
        - qoutation
        - yigchung
    """

    return {_attr_names.SPAN: span}


# ~~~HFML~~~~


def get_start_len(start_marker):
    # unescape
    unescaped_start_marker = start_marker.replace("\\", "")
    return len(unescaped_start_marker)


def _pat(ann_func, start_marker, end_marker, has_text=False, payload_delimiter=None):
    return {
        "start": start_marker + ".",  # dot for tofu-id
        "start_len": get_start_len(start_marker),
        "end": end_marker,
        "has_text": has_text,
        "payload_delimiter": payload_delimiter,
        "payload_dict": copy.copy(ann_func.__kwdefaults__),
    }


HFML_ANN_PATTERN = {
    AnnType.pecha_title: _pat(OnlySpan, "<k1", ">", has_text=True),
    AnnType.correction: _pat(
        Correction, r"\(", r"\)", has_text=True, payload_delimiter=","
    ),
}
