from pathlib import Path

from git import Repo

from openpecha.github_utils import commit, create_orphan_branch
from openpecha.utils import download_pecha, load_yaml

from .exporter.bitext import BitextExporter
from .exporter.po import PoExporter


class Alignment:
    def __init__(self, path=None, id: str = None):
        if not path:
            self.id = id
            self.alignment_repo_path = download_pecha(self.id)
        else:
            self.alignment_repo_path = Path(path)
            self.id = self.alignment_repo_path.stem
        self.metadata = None

    @classmethod
    def from_path(cls, path):
        if not Path(path).is_dir():
            raise FileNotFoundError(f"Alignment repo {path}")
        return cls(path=path)

    @property
    def meta_path(self):
        return self.alignment_repo_path / f"{self.id}.opa" / "meta.yml"

    def _load_metadata(self):
        repo = Repo(self.alignment_repo_path)
        pre_active_branch = repo.active_branch.name
        repo.git.checkout("master")
        metadata = load_yaml(self.meta_path)
        repo.git.checkout(pre_active_branch)
        return metadata

    @property
    def title(self):
        if self.metadata:
            return self.metadata["title"]

        self.metadata = self._load_metadata()
        return self.metadata["title"]

    @property
    def alignment_path(self):
        return self.alignment_repo_path / f"{self.id}.opa" / "Alignment.yml"

    def create(self):
        pass

    def create_po_view(self):
        exporter = PoExporter(self.alignment_path)
        repo = Repo(self.alignment_repo_path)
        if not self.is_po_created(repo):
            create_orphan_branch(
                self.alignment_repo_path, "po", parent_branch="master", type_="opa"
            )
        else:
            repo.git.checkout("po")
        exporter.export(self.alignment_repo_path)
        commit(self.alignment_repo_path, "po file added", not_includes=[], branch="po")
        return self.alignment_repo_path

    def is_po_created(self, repo):
        if "po" in repo.branches:
            return True
        else:
            return False

    def get_po_view(self):
        po_views = {}
        exporter = PoExporter(self.alignment_path)
        repo = Repo(self.alignment_repo_path)
        seg_srcs = exporter.alignment.get("segment_sources", {})
        if seg_srcs:
            if not self.is_po_created(repo):
                self.create_po_view()
            else:
                repo.git.checkout("po")
            for pecha_id, pecha_info in seg_srcs.items():
                pecha_type = pecha_info.get("relation", "")
                pecha_lang = pecha_info.get("lang", "")
                if pecha_type:
                    po_views[pecha_type] = {
                        "path": self.alignment_repo_path / f"{pecha_lang}.po",
                        "lang": pecha_lang,
                    }
        return po_views

    def create_bitext_view(self):
        exporter = BitextExporter(self.alignment_path)
        create_orphan_branch(
            self.alignment_repo_path, "bitext", parent_branch="master", type_="opa"
        )
        exporter.export(self.alignment_repo_path)
        commit(
            self.alignment_repo_path,
            "bitext file added",
            not_includes=[],
            branch="bitext",
        )
        return self.alignment_repo_path
