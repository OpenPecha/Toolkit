import shutil
from pathlib import Path
from typing import Dict, Union

from openpecha.core.layer import Layer, MetaData
from openpecha.utils import dump_yaml


class OpenPechaFS:
    def __init__(self, opf_path):
        self.base_path = "base"
        self.layers_path = "layers"
        self.pecha_id = None
        self._opf_path = opf_path
        self.output_dir = None

    def prepare_save(self, pecha_id, output_dir):
        self.pecha_id = pecha_id
        self.output_dir = output_dir
        self._opf_path = None

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
    def meta_fn(self):
        return self.opf_path / "meta.yml"

    @property
    def index_fn(self):
        return self.opf_path / "index.yml"

    @property
    def assets_path(self):
        return self.opf_path / "assets"

    def save_meta(self, meta: MetaData):
        dump_yaml(eval(meta.json()), self.meta_fn)

    def save_base(self, base: Dict[str, str]):
        for basename, content in base.items():
            base_fn = self._mkdir(self.opf_path / self.base_path) / f"{basename}.txt"
            base_fn.write_text(content)

    def save_layers(self, layers: Dict[str, Layer]):
        for basename, base_layers in layers.items():
            for layername, layer in base_layers.items():
                layer_fn = (
                    self._mkdir(self.opf_path / self.layers_path / basename)
                    / f"{layername.value}.yml"
                )
                dump_yaml(eval(layer.json()), layer_fn)

    def save_index(self, index):
        if not index:
            return
        dump_yaml(index, self.index_fn)

    def save_assets(self, assets):
        for assets_type, content in assets.items():
            assets_type_dir = self.assets_path / assets_type
            assets_type_dir.mkdir(parents=True, exist_ok=True)
            for asset_fn in content:
                asset_fn = Path(asset_fn)
                dest_fn = assets_type_dir / asset_fn.name
                shutil.copyfile(str(asset_fn), str(dest_fn))


class OpenPecha:
    def __init__(
        self,
        base: Dict = {},
        layers: Dict[str, Layer] = {},
        index: Dict = {},
        meta: MetaData = None,
        opf_path: Path = None,
        assets: Dict = {},
    ):
        self._pecha_id = None
        self.base = base
        self.layers = layers
        self._meta = meta
        self.index = index
        self.assets = assets
        self.opfs = OpenPechaFS(opf_path)

    @property
    def id(self):
        if self._pecha_id:
            return self._pecha_id
        self._pecha_id = self.meta.id
        return self._pecha_id

    @property
    def meta(self):
        if self._meta:
            return self._meta
        self._meta = self.opf.read_meta()
        return self._meta

    def get_base(self, basename):
        if basename in self.base:
            return self.base[basename]
        self.base[basename] = self.opfs.get_base(basename)
        return self.base[basename]

    def get_layer(self, basename, layername):
        if basename in self.layers and layername in self.layers[basename]:
            return self.layers[basename][layername]

        self.base[basename] = self.opfs.get_base(basename)
        return self.base[basename]

    @classmethod
    def from_dir(cls, path: Union[str, Path]):
        return cls(opf_path=Path(path))

    def save(self, output_path: Union[str, Path]):
        self.opfs.prepare_save(self.id, Path(output_path))
        self.opfs.save_base(self.base)
        self.opfs.save_layers(self.layers)
        self.opfs.save_index(self.index)
        self.opfs.save_meta(self.meta)
        self.opfs.save_assets(self.assets)
        return self.opfs.opf_path
