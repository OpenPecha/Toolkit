from openpecha.cli import download_pecha
from openpecha.github_utils import commit, create_orphan_branch

from .exporter.bitext import BitextExporter
from .exporter.po import PoExporter
from .segmenters import Segmenter


class Alignment:
    def __init__(self, id=None, segmenter: Segmenter = None):
        self.id = id
        self.segmenter = segmenter
        self.alignment_repo_path = download_pecha(self.id)

    @property
    def alignment_path(self):
        return self.alignment_repo_path / f"{self.id}.opa" / "Alignment.yml"

    def create(self):
        pass

    def create_po_view(self):
        exporter = PoExporter(self.alignment_path)
        create_orphan_branch(self.alignment_repo_path, "po")
        exporter.export(self.alignment_repo_path)
        commit(self.alignment_repo_path, "po file added", branch="po")
        return self.alignment_repo_path

    def create_bitext_view(self):
        exporter = BitextExporter(self.alignment_path)
        create_orphan_branch(self.alignment_repo_path, "bitext")
        exporter.export(self.alignment_repo_path)
        commit(self.alignment_repo_path, "bitext file added", branch="bitext")
        return self.alignment_repo_path
