from pathlib import Path

from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.metadata import InitialCreationType, PechaMetadata
from openpecha.core.pecha import OpenPechaFS

from .. import config


class EmptyEbook:
    def __init__(self, output_path=config.PECHAS_PATH, metadata={}, assets={}) -> None:
        self.output_path = Path(output_path if output_path else config.PECHAS_PATH)
        self.metadata = metadata
        self.meta_fn = None
        self.pecha_path = None
        self.assets = assets
        self.layers = [
            LayerEnum.book_title,
            LayerEnum.sub_title,
            LayerEnum.book_number,
            LayerEnum.author,
            LayerEnum.chapter,
            LayerEnum.citation,
            LayerEnum.tsawa,
            LayerEnum.sabche,
            LayerEnum.yigchung,
        ]

    def get_dummy_layers(self):
        layers = {}
        for layer in self.layers:
            layers[layer] = Layer(
                annotation_type=layer, revision="00001", annotations={}
            )
        return layers

    def create_opf(self, text, id_):
        openpecha = OpenPechaFS(
            base={"v001": text},
            layers={"v001": self.get_dummy_layers()},
            metadata=PechaMetadata(
                initial_creation_type=InitialCreationType.ebook,
                source_metadata=self.metadata,
            ),
            assets=self.assets,
        )

        openpecha.save(output_path=self.output_path)
        self.meta_fn = openpecha.meta_fn
        self.pecha_path = openpecha.opf_path.parent
