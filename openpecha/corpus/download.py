import os

import requests

from openpecha import config
from openpecha.github_utils import get_github_repo
from openpecha import utils



def get_base_vol_list(pecha_repo, pecha_id):
    """Return list of base text file name present in pecha's opf

    Args:
        pecha_repo (repo): pecha repo object
        pecha_id (str): pecha id

    Returns:
        list: list of base text file name
    """
    base_vols = []
    contents = pecha_repo.get_contents(f"./{pecha_id}.opf/base")
    for content_file in contents:
        base_vols.append(content_file.name)
    return base_vols


def download_base_vols(output_path, pecha_id, base_vols):
    """Download and save pecha's base text in output path dir

    Args:
        output_path (Path): output path dir
        pecha_id (sttr): pecha id
        base_vols (list): list of base text in opf
    """
    for base_vol in base_vols:
        base_response = requests.get(
            f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/blob/master/{pecha_id}.opf/base/{base_vol}"
        )
        base_text = base_response.text
        pecha_dir_path = utils._mkdir((output_path / pecha_id))
        (pecha_dir_path / base_vol).write_text(base_text, encoding="utf-8")
        print(f"INFO: {base_vol} download completee...")

def download_corpus(corpus_name, output_path=None):
    """download corpus from openpecha

    Args:
        corpus_name (str): name of corpus on which list of pecha has been prepared in catalog repo of openpecha
        output_path (Path, optional): output path where corpus will be saved. Defaults to None.
    
    Return:
        path: output path
    """
    if not output_path:
        output_path = utils._mkdir(config.BASE_PATH / "corpus")
    output_path = output_path / corpus_name
    corpus_pecha_list = requests.get(
        f"https://raw.githubusercontent.com/OpenPecha/catalog/master/data/corpus/{corpus_name}.txt"
    )
    corpus_pecha_ids = corpus_pecha_list.text.splitlines()
    for pecha_id in corpus_pecha_ids:
        pecha_repo = get_github_repo(
            pecha_id, org_name="OpenPecha", token=os.environ.get("GITHUB_TOKEN")
        )
        base_vols = get_base_vol_list(pecha_repo, pecha_id)
        download_base_vols(output_path, pecha_id, base_vols)
    return output_path
