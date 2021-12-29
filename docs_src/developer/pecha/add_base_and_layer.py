from openpecha.core.annotations import Citation, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPecha

ann = Citation(span=Span(start=10, end=20))
layer = Layer(annotation_type=LayerEnum.citation)
layer.add_annotation(ann)

pecha = OpenPecha()
base_name = pecha.set_base("base content")

pecha.set_layer(base_name, layer)

assert pecha.layers[base_name][LayerEnum.citation].id == layer.id
