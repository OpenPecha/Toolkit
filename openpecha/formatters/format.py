'''
This module contains format variable for all the annotations
'''

__all__ = ['Layer', 'Page', 'Text', 'Error', 'Note', 'CrossVolSpan', 'SubText', 'Peydurma']

# General layer format
Layer = {
    'id': None,              # Uique id for annotation of specific Pecha or Abstract work. type: str
    'annotation_type': None, # Name of annotation, type: str
    'revision': None,             # Revision number. type: int
    'annotations': []            # Annotations are stored in list . type: list
}

# Span of the annotation
Span = {
    'start': None,     # String index of starting character of the the annotation. type: int
    'end': None,       # String index of the ending character of the annotation. type: int 
}

# Page annotation
Page = {
    'id': None,             # Unique id for particular instance of annotation of a layer. type: str
    'span': Span,           # Span of particualr annotation, type: Span
    'page_index': None,     # Page number based on Volume specified in `part_of`. type: int
    'page_info': None,      # Page information. type: str
    'reference': None,      # Any reference of page, eg: img_url. type: str
}

# Cross vol Span
CrossVolSpan = {
    'vol': None,
    'span': Span
}

# Sub_text annotation
SubText = {
    'id': None,              # Unique id for the sub_text
    'span': Span,            # span of the sub_text
    'base': None,            # Which volume the sub_text is from
    'sub_text_index': None   # index of the sub_text
}

# Text annotation
Text = {
    'id': None,             # Unique id for particular Text. type: str
    'span': [],             # list of CrossVolSpan
    'text_index': None,     # Order of the `sub_text`. type: int
    'sub_text': []          # list of SubText
}

# Error and Suggestion annotation
Error = {
    'id': None,             # Unque id for particular error text. type: int
    'span': Span,           # Span of error text. type: Span
    'correction': None,     # Correct text suggestion. type: str
    'certainty': None       # Certainty of the suggested correct text. type: int
}

Peydurma = {
    'id': None,
    'span': Span
}

# Note
Note = {
    'id': None,
    'span': Span,
    'note': None
}