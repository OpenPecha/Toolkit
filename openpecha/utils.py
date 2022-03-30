"""Utilities functions
"""
import gzip
import io
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict

import yaml
from git import GIT_OK, Repo
from git.cmd import GitCommandError

from openpecha import config, storages
from openpecha.exceptions import PechaNotFound
from openpecha.github_utils import create_release
from openpecha.storages import GithubStorage, setup_auth_for_old_repo

INFO = "[INFO] {}"


def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj

def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path
    
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


def dump_yaml(data: Dict, output_fn: Path) -> Path:
    with output_fn.open("w", encoding="utf-8") as fn:
        yaml.dump(
            data,
            fn,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            Dumper=yaml.CSafeDumper,
        )
    return output_fn


def load_yaml(fn: Path) -> None:
    return yaml.load(fn.open(encoding="utf-8"), Loader=yaml.CSafeLoader)


def _eval_branch(repo, branch):
    """return default branch as fallback branch."""
    if branch in repo.refs or f"origin/{branch}" in repo.refs:
        return branch
    elif "main" in repo.refs:
        return "main"
    else:
        return "master"


def download_pecha(pecha_id, out_path=None, needs_update=True, branch="main"):
    # clone the repo
    pecha_url = f"{config.GITHUB_ORG_URL}/{pecha_id}.git"
    if out_path:
        out_path = Path(out_path)
        out_path.mkdir(exist_ok=True, parents=True)
        pecha_path = out_path / pecha_id
    else:
        pecha_path = config.PECHAS_PATH / pecha_id

    if pecha_path.is_dir():  # if repo is already exits at local then try to pull
        repo = Repo(str(pecha_path))
        branch = _eval_branch(repo, branch)
        repo.git.checkout(branch)
        if needs_update:
            print(INFO.format(f"Updating {pecha_id} ..."))
            repo.git.pull("origin", branch)
    else:
        print(INFO.format(f"Downloading {pecha_id} ..."))
        try:
            Repo.clone_from(pecha_url, str(pecha_path))
        except GitCommandError:
            raise PechaNotFound(f"Pecha with id {pecha_id} doesn't exist")
        repo = Repo(str(pecha_path))
        branch = _eval_branch(repo, branch)
        repo.git.checkout(branch)

    # setup auth
    storage = GithubStorage()
    setup_auth_for_old_repo(repo, org=storage.org_name, token=storage.token)

    return pecha_path
