import os
from pathlib import Path

import requests

from openpecha.github_utils import get_github_repo


def get_base_vol_list(pecha_repo, pecha_id):
    base_vols = []
    contents = pecha_repo.get_contents(f"./{pecha_id}.opf/base")
    for content_file in contents:
        base_vols.append(content_file.name)
    return base_vols


def download_base_vols(output_path, pecha_id, base_vols):
    for base_vol in base_vols:
        base_response = requests.get(
            f"https://github.com/OpenPecha/{pecha_id}/blob/master/{pecha_id}.opf/base/{base_vol}"
        )
        base_text = base_response.text
        (output_path / pecha_id).mkdir(exist_ok=True)
        (output_path / pecha_id / base_vol).write_text(base_text, encoding="utf-8")
        print(f"INFO: {base_vol} download completee...")


def download_corpus(corpus_name, output_path=None):
    if not output_path:
        Path("./openpecha_corpus").mkdir(exist_ok=True)
        output_path = Path().home() / "openpecha_corpus"
    corpus_pecha_list = requests.get(
        f"https://raw.githubusercontent.com/OpenPecha/catalog/master/data/{corpus_name}/pecha_list.txt"
    )
    corpus_pecha_ids = corpus_pecha_list.text.splitlines()
    for pecha_id in corpus_pecha_ids:
        pecha_repo = get_github_repo(
            pecha_id, org_name="OpenPecha", token=os.environ.get("GITHUB_TOKEN")
        )
        base_vols = get_base_vol_list(pecha_repo, pecha_id)
        download_base_vols(output_path, pecha_id, base_vols)
