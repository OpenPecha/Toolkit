from pathlib import Path


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


# Path
BASE_PATH = _mkdir(Path.home() / ".openpecha")
PECHAS_PATH = _mkdir(BASE_PATH / "pechas")

# Pecha
PECHA_PREFIX = "P"
N_SIG = 6  # no. of significant digits for pecha id
