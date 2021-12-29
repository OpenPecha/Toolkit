from openpecha.core.layer import Layer, LayerEnum

layer = Layer(annotation_type=LayerEnum.citation)

assert layer.annotation_type == LayerEnum.citation
