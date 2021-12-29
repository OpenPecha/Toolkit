from openpecha.core.layer import Layer, LayerEnum

layer = Layer(annotation_type=LayerEnum.citation)

assert layer.revision == "00001"

layer.bump_revision()

assert layer.revision == "00002"
