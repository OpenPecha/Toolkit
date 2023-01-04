from openpecha.core.annotations import Citation, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.metadata import InitialCreationType, InitialPechaMetadata
from openpecha.core.pecha import OpenPechaFS

# create new pecha
metadata = InitialPechaMetadata(initial_creation_type=InitialCreationType.input)
pecha = OpenPechaFS(path="<path_to_pecha>", metadata=metadata)

# create a simple layer
ann = Citation(span=Span(start=10, end=20))
layer = Layer(annotation_type=LayerEnum.citation)
layer.set_annotation(ann)

base_name = pecha.set_base("base content")
pecha.set_layer(base_name, layer)

# pecha.save()
