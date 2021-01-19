"""Utilities functions
"""
import gzip
import io
import shutil
from collections import defaultdict

import yaml

from openpecha.github_utils import create_release


def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


def ocr_result_input(path):
    return path


def create_release_with_assets(path):
    asset_paths = []
    for asset_path in (path / "releases").iterdir():
        shutil.make_archive(asset_path, "zip", asset_path)
        asset_paths.append(f"{str(asset_path)}.zip")

    create_release(path.name, asset_paths=asset_paths)


class Vol2FnManager:
    def __init__(self, metadata):
        self.name = "vol2fn"
        self.vol_num = 0
        self.vol2fn = self._get_vol2fn(metadata)
        self.fn2vol = {fn: vol for vol, fn in self.vol2fn.items()}

    def _get_vol2fn(self, metadata):
        if self.name in metadata:
            return metadata[self.name]
        else:
            return defaultdict(dict)

    def get_fn(self, vol):
        return self.vol2fn.get(vol)

    def get_vol_id(self, fn):
        vol_id = self.fn2vol.get(fn)
        if vol_id:
            return vol_id
        else:
            self.vol_num += 1
            vol_id = f"v{self.vol_num:03}"
            self.vol2fn[vol_id] = fn
            return vol_id


def dump_yaml(data, output_fn):
    with output_fn.open("w") as fn:
        yaml.dump(
            data, fn, default_flow_style=False, sort_keys=False, allow_unicode=True
        )


def load_yaml(fn):
    return yaml.safe_load(fn.open())
