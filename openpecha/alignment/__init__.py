from pathlib import Path

from openpecha.cli import download_pecha


class Alignment:
    def __init__(self, path=None, id: str = None):
        if not path:
          self.id = id
          self.alignment_repo_path = download_pecha(self.id)
        else:
          self.alignment_repo_path = Path(path)
          self.id = self.alignment_repo_path.stem

    @classmethod
    def from_path(cls, path):
      if not Path(path).is_dir():
        raise FileNotFoundError(f"Alignment repo {path}")
      return cls(path=path)

    @property
    def alignment_path(self):
        return self.alignment_repo_path / f"{self.id}.opa" / "Alignment.yml"

    def create(self):
        pass

