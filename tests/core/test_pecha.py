from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, MetaData
from openpecha.core.pecha import OpenPecha


def test_init_pecha():
    openpecha = OpenPecha(
        base={"v001": "this is base"},
        layers={
            "v001": {
                LayerEnum.citation: Layer(
                    annotation_type=LayerEnum.citation, revision="00001", annotations={}
                )
            }
        },
        meta=MetaData(id="P000001", initial_creation_type=InitialCreationEnum.ebook),
    )
    assert openpecha.meta
    assert openpecha.get_base("v001")
    assert openpecha.get_layer("v001", LayerEnum.citation)
    assert openpecha.save("output")
