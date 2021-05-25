import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Union

from openpecha import config
from openpecha.core.layer import Layer, LayerEnum, MetaData
from openpecha.utils import dump_yaml, load_yaml


class OpenPecha:
    def __init__(
        self,
        base: Dict[str, str] = {},
        layers: Dict[str, Dict[LayerEnum, Layer]] = defaultdict(dict),
        index: Layer = None,
        meta: MetaData = None,
        assets: Dict[str, List[Union[str, Path]]] = {},
        components: Dict[str, List[Layer]] = {},
    ):
        self._pecha_id = None
        self.base = base
        self.layers = layers
        self._meta = meta
        self._index = index
        self.assets = assets
        self._components = components

    def reset_base_and_layers(self):
        self.base = {}
        self.layers = defaultdict(dict)

    @property
    def pecha_id(self) -> str:
        if self._pecha_id:
            return self._pecha_id
        self._pecha_id = self.meta.id
        return self._pecha_id

    @property
    def meta(self) -> MetaData:
        if self._meta:
            return self._meta
        self._meta = MetaData.parse_obj(self.read_meta_file())
        return self._meta

    @property
    def index(self) -> Layer:
        if self._index:
            return self._index
        self._index = Layer.parse_obj(self.read_index_file())
        return self._index

    @property
    def components(self) -> Dict[str, List[LayerEnum]]:
        if self._components:
            return self._components
        self._components = self._read_components()
        return self._components

    def get_base(self, base_name: str) -> str:
        if base_name in self.base:
            return self.base[base_name]
        self.base[base_name] = self.read_base_file(base_name)
        return self.base[base_name]

    def get_layer(self, base_name: str, layer_name: LayerEnum) -> Layer:
        if base_name in self.layers and layer_name in self.layers[base_name]:
            layer = self.layers[base_name][layer_name]
            if layer:
                return layer

        layer_dict = self.read_layers_file(base_name, layer_name.value)
        if layer_dict:
            layer = Layer.parse_obj(layer_dict)
        else:
            layer = Layer(annotation_type=layer_name)
        self.layers[base_name][layer_name] = layer
        return layer


class OpenPechaFS(OpenPecha):
    def __init__(self, opf_path=None, **kwargs):
        self._opf_path = Path(opf_path) if opf_path else opf_path
        self.output_dir = None
        super().__init__(**kwargs)

    @staticmethod
    def _mkdir(path: Path):
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def opf_path(self) -> Path:
        if self._opf_path:
            return self._opf_path
        self._opf_path = self.output_dir / self.pecha_id / f"{self.pecha_id}.opf"
        return self._opf_path

    @property
    def base_path(self) -> Path:
        return self.opf_path / "base"

    @property
    def layers_path(self) -> Path:
        return self.opf_path / "layers"

    @property
    def meta_fn(self) -> Path:
        return self.opf_path / "meta.yml"

    @property
    def index_fn(self) -> Path:
        return self.opf_path / f"{LayerEnum.index.value}.yml"

    @property
    def assets_path(self) -> Path:
        return self.opf_path / "assets"

    def read_base_file(self, base_name: str) -> str:
        return (self.base_path / f"{base_name}.txt").read_text(encoding="utf-8")

    def read_layers_file(
        self, base_name: str, layer_name: LayerEnum
    ) -> Union[Dict, None]:
        layer_fn = self.layers_path / base_name / f"{layer_name}.yml"
        if layer_fn.is_file():
            return load_yaml(layer_fn)

    def read_meta_file(self) -> Dict:
        return load_yaml(self.meta_fn)

    def read_index_file(self) -> Dict:
        if not self.index_fn.is_file():
            raise FileNotFoundError
        return load_yaml(self.index_fn)

    def _read_components(self):
        res = {}
        for vol_dir in self.layers_path.iterdir():
            res[vol_dir.name] = list(
                map(lambda fn: LayerEnum(fn.stem), vol_dir.iterdir())
            )
        return res

    def save_meta(self):
        dump_yaml(json.loads(self.meta.json()), self.meta_fn)

    def save_single_base(self, base_name: str, content: str):
        base_fn = self._mkdir(self.base_path) / f"{base_name}.txt"
        base_fn.write_text(content)

    def save_base(self):
        for base_name, content in self.base.items():
            self.save_single_base(base_name, content)

    def save_layer(self, base_name: str, layer_name: LayerEnum, layer: Layer):
        layer_fn = self._mkdir(self.layers_path / base_name) / f"{layer_name.value}.yml"
        dump_yaml(json.loads(layer.json()), layer_fn)

    def save_layers(self):
        for base_name, base_layers in self.layers.items():
            for layer_name, layer in base_layers.items():
                self.save_layer(base_name, layer_name, layer)

    def save_index(self):
        try:
            dump_yaml(json.loads(self.index.json()), self.index_fn)
        except FileNotFoundError:
            pass

    def save_assets(self):
        for assets_type, content in self.assets.items():
            assets_type_dir = self.assets_path / assets_type
            assets_type_dir.mkdir(parents=True, exist_ok=True)
            for asset_fn in content:
                asset_fn = Path(asset_fn)
                dest_fn = assets_type_dir / asset_fn.name
                shutil.copyfile(str(asset_fn), str(dest_fn))

    def save(self, output_path: Union[str, Path] = config.PECHAS_PATH):
        self.output_dir = Path(output_path)
        self._opf_path = None

        self.save_base()
        self.save_layers()
        self.save_index()
        self.save_meta()
        self.save_assets()
        return self.opf_path

    def update_base(self, base_name: str, content: str):
        self.save_single_base(base_name, content)

    def update_layer(self, base_name: str, layer_name: LayerEnum, layer: Layer):
        old_layer = self.get_layer(base_name, layer_name)
        old_layer.bump_revision()
        old_layer.annotations = layer.annotations
        self.save_layer(base_name, layer_name, old_layer)

    def reset_layer(self, base_name: str, layer_name: LayerEnum):
        print("reset->", layer_name.value)
        layer = self.get_layer(base_name, layer_name)
        layer.reset()
        self.save_layer(base_name, layer_name, layer)
        self.layers[base_name][layer_name] = None

    def reset_layers(self, base_name: str, exclude: List[LayerEnum] = []):
        for layer_name in self.components[base_name]:
            if layer_name in exclude:
                continue
            self.reset_layer(base_name, layer_name)
