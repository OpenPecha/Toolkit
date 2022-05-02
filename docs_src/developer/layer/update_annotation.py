from openpecha.core.annotations import Citation, Span
from openpecha.core.layer import Layer, LayerEnum

layer = Layer(annotation_type=LayerEnum.citation)
ann = Citation(span=Span(start=10, end=20))
layer.set_annotation(ann)

# update `ann`
old_ann = layer.get_annotation(ann.id)
old_ann.span.start = 15
layer.set_annotation(old_ann)

new_ann = layer.get_annotation(old_ann.id)

# assert new_ann.span.start == 16
