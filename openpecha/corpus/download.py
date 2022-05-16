import csv
import io
import json
import os
import zipfile
from multiprocessing.sharedctypes import Value

import requests
from tqdm import tqdm

from openpecha import config, utils
from openpecha.github_utils import get_github_repo


def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    github_keys_path = config.BASE_PATH / "keys" / "github.json"
    if github_keys_path.is_file():
        keys = json.load(github_keys_path.open())
        return keys["download"]

    url = "https://github.com/OpenPecha-dev/keys/releases/download/v1/keys.zip"
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(path=str(config.BASE_PATH))
    keys = json.load(github_keys_path.open())
    return keys["download"]


def get_base_vol_list(pecha_repo, pecha_id):
    """Return list of base text file name present in pecha's opf

    Args:
        pecha_repo (repo): pecha repo object
        pecha_id (str): pecha id

    Returns:
        list: list of base text file name
    """
    base_vols = []
    contents = pecha_repo.get_contents(f"/{pecha_id}.opf/base")
    for content_file in contents:
        base_vols.append(content_file.name)
    return base_vols


def download_base_vols(output_path, pecha_id, base_vols, session):
    """Download and save pecha's base text in output path dir

    Args:
        output_path (Path): output path dir
        pecha_id (sttr): pecha id
        base_vols (list): list of base text in opf
    """
    for base_vol in base_vols:
        base_response = session.get(
            f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/base/{base_vol}"
        )
        base_text = base_response.text
        pecha_dir_path = utils._mkdir((output_path / pecha_id))
        (pecha_dir_path / base_vol).write_text(base_text, encoding="utf-8")


def get_corpus_catalog(corpus_name, session):
    catalog_url = (
        f"https://github.com/OpenPecha/corpus_catalog/raw/main/data/{corpus_name}.csv"
    )
    r = session.get(catalog_url, stream=True)

    if r.status_code != requests.codes.OK:
        ValueError(f"Corpus with name `{corpus_name}` doesn't exists")

    lines = (line.decode("utf-8") for line in r.iter_lines())
    csv_reader = csv.reader(lines)
    next(csv_reader, None)  # skip headers
    for row in csv_reader:
        yield row


def get_request_session():
    session = requests.Session()
    token = get_github_token()
    session.headers["Authorization"] = f"token {token}"
    return session


def download_corpus(
    corpus_name, output_path=utils._mkdir(config.BASE_PATH / "corpus"), replace=False
):
    """download corpus from openpecha

    Args:
        corpus_name (str): name of corpus on which list of pecha has been prepared in catalog repo of openpecha
        output_path (Path, optional): output path where corpus will be saved. Defaults to None.

    Return:
        path: output path
    """
    corpus_output_path = output_path / corpus_name
    session = get_request_session()
    corpus_catalog = get_corpus_catalog(corpus_name, session)
    print(list(corpus_catalog)[0])
    # corpus_pecha_ids = corpus_pecha_list.text.splitlines()
    # for pecha_id in tqdm(corpus_pecha_ids):
    #     if (output_path / pecha_id).is_dir() and not replace:
    #         continue
    #     pecha_repo = get_github_repo(pecha_id, org_name="OpenPecha", token=token)
    #     base_vols = get_base_vol_list(pecha_repo, pecha_id)
    #     download_base_vols(output_path, pecha_id, base_vols, session)
    # return output_path


if __name__ == "__main__":
    download_corpus("literary_bo")
