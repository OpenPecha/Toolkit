from openpecha.core.annotations import Citation, Span
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS

# create new pecha
metadata = PechaMetaData(initial_creation_type=InitialCreationEnum.input)
pecha = OpenPechaFS(metadata=metadata)

# create a simple layer
ann = Citation(span=Span(start=10, end=20))
layer = Layer(annotation_type=LayerEnum.citation)
layer.set_annotation(ann)

base_name = pecha.set_base("base content")
pecha.set_layer(base_name, layer)

pecha.save()
