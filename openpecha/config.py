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

GITHUB_ORG_URL = "https://github.com/OpenPecha"

# Work
WORKS_REPO_NAME = "works"
OP2BDRC_WORK_MAPPING_URL = (
    "https://raw.githubusercontent.com/OpenPecha/works/main/mappings/bdrc.csv"
)
