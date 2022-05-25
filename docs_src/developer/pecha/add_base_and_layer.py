from openpecha.core.annotations import Citation, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaFS

pecha = OpenPechaFS(path="<path_to_pecha>")

# create a simple layer
ann = Citation(span=Span(start=10, end=20))
layer = Layer(annotation_type=LayerEnum.citation)
layer.set_annotation(ann)

base_name = pecha.set_base("base content", metadata={"title": "title", "order": 1})
pecha.set_layer(base_name, layer)

pecha.save()

assert pecha.layers[base_name][LayerEnum.citation].id == layer.id
