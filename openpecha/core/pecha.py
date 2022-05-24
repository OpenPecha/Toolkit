import json
import shutil
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Union

from openpecha import blupdate, config
from openpecha.core import ids
from openpecha.core.annotations import BaseAnnotation, Span
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata, SpanINFO
from openpecha.storages import GithubStorage, Storage
from openpecha.utils import download_pecha, dump_yaml, load_yaml


class OpenPecha:
    def __init__(
        self,
        base: Dict[str, str] = {},
        layers: Dict[str, Dict[LayerEnum, Layer]] = defaultdict(dict),
        index: Layer = None,
        meta: PechaMetadata = None,
        metadata: PechaMetadata = None,
        assets: Dict[str, List[Union[str, Path]]] = {},
        components: Dict[str, List[Layer]] = {},
    ):
        self._pecha_id = None
        self.base = base
        self.layers = layers
        self._meta = self.__handle_old_metadata_attr(meta, metadata)
        self._index = index
        self.assets = assets
        self._components = components
        self.current_base_order = 1

    def __str__(self):
        return f"OpenPecha:{self.pecha_id}"

    def __handle_old_metadata_attr(self, old, new):
        if not old and not new:
            return

        if new:
            return new

        warnings.warn(
            "use `metadata` attr instead of `meta` to set pecha metadata",
            DeprecationWarning,
            stacklevel=3,
        )
        return old

    @property
    def about(self):
        source_metadata = []
        for val in self.meta.source_metadata.values():
            if not isinstance(val, (str, int)):
                continue
            source_metadata.append(val)
        return ", ".join(source_metadata)

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
    def meta(self) -> PechaMetadata:
        if self._meta:
            return self._meta
        self._meta = PechaMetadata.parse_obj(self.read_meta_file())
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

    def _get_base_name(self) -> str:
        return ids.get_base_id()

    def _set_base_metadata(self, base_name: str, metadata: Dict) -> None:
        metadata.update({"base_file": f"{base_name}.txt"})
        if "base" not in self.meta.source_metadata:
            self.meta.source_metadata["base"] = {}
        self.meta.source_metadata["base"][base_name] = metadata

    def get_base(self, base_name: str) -> str:
        if base_name in self.base:
            return self.base[base_name]
        self.base[base_name] = self.read_base_file(base_name)
        return self.base[base_name]

    def get_base_metadata(self, base_name: str) -> str:
        self.meta.source_metadata["base"].get(base_name)

    def set_base(self, content: str, base_name: str = None, metadata: Dict = {}) -> str:
        """Create new base with `content` if `base_name` is not
        given otherwise overwrites it and return base_name.
        """
        if base_name and base_name in self.base:
            blupdate.update_single_base(self, base_name, content)
            self.base[base_name] = content
        else:
            base_name = self._get_base_name()
            self.base[base_name] = content
            self._set_base_metadata(base_name, metadata)
        return base_name

    def get_layers(self, base_name: str) -> Layer:
        for layer_name in self.components[base_name]:
            yield self.get_layer(base_name, layer_name)

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

    def update_metadata(self):
        self.meta.update_last_modified_date()

    def set_layer(self, base_name: str, layer: Layer):
        if base_name not in self.base:
            raise ValueError(f"set base for {base_name} first")

        self.layers[base_name][layer.annotation_type] = layer

    def __find_span_layers(
        self, base_name: str, span: Span, layers: List[LayerEnum]
    ) -> Dict[LayerEnum, List[BaseAnnotation]]:
        result = defaultdict(list)
        for layer_name in layers:
            if layer_name not in self.components[base_name]:
                result[layer_name] = []

            layer = self.get_layer(base_name, layer_name)
            for ann in layer.get_annotations():
                is_ann_found = False
                base_str = self.get_base(base_name)
                if ann.span.start >= span.start and ann.span.end <= span.end:
                    is_ann_found = True
                elif ann.span.end >= span.start and ann.span.start < span.start:
                    is_ann_found = True
                    ann.span.start = span.start
                elif ann.span.start <= span.end and ann.span.end > span.end:
                    is_ann_found = True
                    ann.span.end = span.end

                if is_ann_found:
                    ann.span.start -= span.start
                    ann.span.end -= span.start
                    result[layer_name].append(ann)

        return result

    def get_span_info(
        self, base_name: str, span: Span, layers: List[LayerEnum] = []
    ) -> SpanINFO:
        base_str = self.get_base(base_name)
        span_str = base_str[span.start : span.end + 1]
        layers = self.__find_span_layers(base_name, span, layers)
        return SpanINFO(text=span_str, layers=layers, metadata=self.meta)


class OpenPechaFS(OpenPecha):
    """Class to represent opf pecha on file-system.

    Note:
        Either use pecha_id or `path` attribute to create
        instance, `pecha_id` for downloading/updating pecha and
        `path` for local pecha.

    Attributes:
        pecha_id(str): id of openpecha pecha.
        path (str): path to local pecha root or pecha .opf path.
        storage (Storage): storage obj for saving at remote.
    """

    def __init__(
        self, pecha_id: str = None, path: str = None, storage: Storage = None, **kwargs
    ):
        self._opf_path = self.get_opf_path(pecha_id, path)
        self.output_dir = None
        self.storage = storage
        super().__init__(**kwargs)

    @staticmethod
    def get_opf_path(pecha_id, path: str) -> Path:
        """convert pecha path to pecha's opf path"""
        if not pecha_id and not path:
            return

        if not path:
            return download_pecha(pecha_id)

        path = Path(path)
        if path.name.endswith(".opf"):
            return path
        path = path / f"{path.name}.opf"
        if not path.is_dir():
            raise FileNotFoundError(f"Pecha not found at: {path}")
        return path

    @staticmethod
    def _mkdir(path: Path):
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def opf_path(self) -> Path:
        if self._opf_path:
            return self._opf_path
        self._opf_path = self.pecha_path / f"{self.pecha_id}.opf"
        return self._opf_path

    @property
    def pecha_path(self) -> Path:
        return self.output_dir / self.pecha_id

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

    def save_single_base(self, base_name: str, content: str = None):
        if not content:
            content = self.base[base_name]
        base_fn = self._mkdir(self.base_path) / f"{base_name}.txt"
        base_fn.write_text(content)

    def save_base(self):
        for base_name, content in self.base.items():
            self.save_single_base(base_name, content)

    def save_layer(self, base_name: str, layer_name: LayerEnum, layer: Layer):
        layer_fn = self._mkdir(self.layers_path / base_name) / f"{layer_name.value}.yml"
        dump_yaml(json.loads(layer.json()), layer_fn)
        return layer_fn

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
        self.set_base(content, base_name)
        self.save_single_base(base_name)
        self.update_metadata()

    def update_layer(self, base_name: str, layer_name: LayerEnum, layer: Layer):
        old_layer = self.get_layer(base_name, layer_name)
        old_layer.bump_revision()
        old_layer.annotations = layer.annotations
        self.save_layer(base_name, layer_name, old_layer)
        self.update_metadata()

    def reset_layer(self, base_name: str, layer_name: LayerEnum):
        layer = self.get_layer(base_name, layer_name)
        layer.reset()
        self.save_layer(base_name, layer_name, layer)
        self.layers[base_name][layer_name] = None

    def reset_layers(self, base_name: str, exclude: List[LayerEnum] = []):
        for layer_name in self.components[base_name]:
            if layer_name in exclude:
                continue
            self.reset_layer(base_name, layer_name)

    def publish(self):
        if not self.storage:
            self.storage = GithubStorage()
        self.storage.add_dir(path=self.pecha_path, description=self.about)

    def remove(self):
        self.storage.remove_dir_with_path(name=self.pecha_path)
