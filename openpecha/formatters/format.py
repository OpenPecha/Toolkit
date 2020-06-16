"""
This module contains format variable for all the annotations
"""

from collections import namedtuple

__all__ = [
    "Layer",
    "Page",
    "Text",
    "Correction",
    "ErrorCandidate",
    "CrossVolSpan",
    "SubText",
    "Peydurma",
    "Chapter",
    "Tsawa",
    "Quotation",
    "Sabche",
    "Yigchung",
    "Book_title",
    "Author",
]

# General layer format
Layer = {
    "id": None,  # Uique id for annotation of specific Pecha or Abstract work. type: str
    "annotation_type": None,  # Name of annotation, type: str
    "revision": None,  # Revision number. type: int
    "annotations": {},  # Annotations are stored in list . type: list
}

# Span of the annotation
Span = {
    "start": None,  # String index of starting character of the the annotation. type: int
    "end": None,  # String index of the ending character of the annotation. type: int
}

# Page annotation
Page = {
    "span": Span,  # Span of particualr annotation, type: Span
    "page_index": None,  # Page number based on Volume specified in `part_of`. type: int
    "page_info": None,  # Page information. type: str
    "reference": None,  # Any reference of page, eg: img_url. type: str
}

# Cross vol Span
CrossVolSpan = {"vol": None, "span": Span}

# Sub_text annotation
SubText = {"work": None, "span": []}  # index of the sub_text  # span of the sub_text

# Text annotation
Text = {
    "work": None,  # id of the `text`. type: int
    "parts": [],  # list of SubText
    "span": [],  # list of CrossVolSpan
}

# Error and Suggestion annotation
Correction = {
    "correction": None,  # Correct text suggestion. type: str
    "certainty": None,  # Certainty of the suggested correct text. type: int
    "span": Span,  # Span of error text. type: Span
}

ErrorCandidate = {"span": Span}

# Note
Peydurma = {"note": None, "span": Span}

# Book titlle and author
Book_title = {"span": Span}
Author = {"span": Span}

# Chapter
Chapter = {"span": Span}

# Tsawa
Tsawa = {"span": Span}

# Quotation
Quotation = {"span": Span}

# Sabche
Sabche = {"span": Span}

# Yigchung:
Yigchung = {"span": Span}
