import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Union

from openpecha import config
from openpecha.core.layer import Layer, LayersEnum, MetaData
from openpecha.utils import dump_yaml, load_yaml


class OpenPecha:
    def __init__(
        self,
        base: Dict = {},
        layers: Dict[str, Dict[LayersEnum, Layer]] = defaultdict(dict),
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

    @property
    def pecha_id(self):
        if self._pecha_id:
            return self._pecha_id
        self._pecha_id = self.meta.id
        return self._pecha_id

    @property
    def meta(self):
        if self._meta:
            return self._meta
        self._meta = MetaData.parse_obj(self.read_meta_file())
        return self._meta

    @property
    def index(self):
        if self._index:
            return self._index
        self._index = Layer.parse_obj(self.read_index_file())
        return self._index

    @property
    def components(self):
        if self._components:
            return self._components
        self._components = self._read_components()
        return self._components

    def get_base(self, basename):
        if basename in self.base:
            return self.base[basename]
        self.base[basename] = self.read_base_file(basename)
        return self.base[basename]

    def get_layer(self, basename, layername):
        if basename in self.layers and layername in self.layers[basename]:
            return self.layers[basename][layername]

        self.layers[basename][layername] = Layer.parse_obj(
            self.read_layers_file(basename, layername.value)
        )
        return self.layers[basename][layername]


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
    def opf_path(self):
        if self._opf_path:
            return self._opf_path
        self._opf_path = self.output_dir / self.pecha_id / f"{self.pecha_id}.opf"
        return self._opf_path

    @property
    def base_path(self):
        return self.opf_path / "base"

    @property
    def layers_path(self):
        return self.opf_path / "layers"

    @property
    def meta_fn(self):
        return self.opf_path / "meta.yml"

    @property
    def index_fn(self):
        return self.opf_path / f"{LayersEnum.index.value}.yml"

    @property
    def assets_path(self):
        return self.opf_path / "assets"

    def read_base_file(self, basename):
        return (self.base_path / f"{basename}.txt").read_text(encoding="utf-8")

    def read_layers_file(self, basename, layername):
        return load_yaml(self.layers_path / basename / f"{layername}.yml")

    def read_meta_file(self):
        return load_yaml(self.meta_fn)

    def read_index_file(self):
        if not self.index_fn.is_file():
            raise FileNotFoundError
        return load_yaml(self.index_fn)

    def _read_components(self):
        res = {}
        for vol_dir in self.layers_path.iterdir():
            res[vol_dir.name] = list(
                map(lambda fn: LayersEnum(fn.stem), vol_dir.iterdir())
            )
        return res

    def save_meta(self):
        dump_yaml(json.loads(self.meta.json()), self.meta_fn)

    def save_base(self):
        for basename, content in self.base.items():
            base_fn = self._mkdir(self.base_path) / f"{basename}.txt"
            base_fn.write_text(content)

    def save_layer(self, basename, layername, layer):
        layer_fn = self._mkdir(self.layers_path / basename) / f"{layername}.yml"
        dump_yaml(json.loads(layer.json()), layer_fn)

    def save_layers(self):
        for basename, base_layers in self.layers.items():
            for layername, layer in base_layers.items():
                layer_fn = (
                    self._mkdir(self.layers_path / basename) / f"{layername.value}.yml"
                )
                dump_yaml(json.loads(layer.json()), layer_fn)

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
