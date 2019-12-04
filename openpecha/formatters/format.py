'''
This module contains format variable for all the annotations
'''

__all__ = ['Layer', 'Page', 'Text', 'Error', 'Yigchung']

# General layer format
Layer = {
    'id': None,              # Uique id for annotation of specific Pecha or Abstract work. type: str
    'annotation_type': None, # Name of annotation, type: str
    'rev': None,             # Revision number. type: int
    'content': []            # Annotations are stored in list . type: list
}

# Span of the annotation
Span = {
    'start_char': None,     # String index of starting character of the the annotation. type: int
    'end_char': None,       # String index of the ending character of the annotation. type: int 
}

# Page annotation
Page = {
    'id': None,             # Unique id for particular instance of annotation of a layer. type: str
    'span': Span,           # Span of particualr annotation, type: Span
    'part_of': None,        # Volume number to which the page is from. eg: `base/v001.txt`. type: str
    'part_index': None,     # Page number based on Volume specified in `part_of`. type: int
    'payload': None,        # Page information. type: str
    'ref': None,            # Any reference of page, eg: img_url. type: str
}

# Text annotation
Text = {
    'id': None,             # Unique id for particular Text. type: str
    'type': None,           # Whether annotation is `text` or `sub_text`. type: str
    'span': Span,           # Span of `text` or `sub_text`,
    'part_of': None,
    'part_index': None,     # Order of the `sub_text`. type: int
}

# Error and Suggestion annotation
Error = {
    'id': None,             # Unque id for particular error text. type: int
    'span': Span,           # Span of error text. type: Span
    'type': None,           # Ambiguous or absolute error 
    'correction': None,     # Correct text suggestion. type: str
    'certainty': None       # Certainty of the suggested correct text. type: int
}

# Yigchung
Yigchung = {
    'id': None,
    'span': Span
}