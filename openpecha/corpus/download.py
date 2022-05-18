import csv
import io
import json
import logging
import os
import shutil
import sys
import zipfile

import requests
from genericpath import exists
from tqdm import tqdm

from openpecha import config, utils

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


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
        return ValueError(f"Corpus with name `{corpus_name}` doesn't exists")

    lines = (line.decode("utf-8") for line in r.iter_lines())
    csv_reader = csv.reader(lines)
    next(csv_reader, None)  # skip headers
    for row in csv_reader:
        yield row


def get_corpus_items_count(corpus_name, session):
    url = (
        f"https://github.com/OpenPecha/corpus_catalog/raw/main/data/{corpus_name}.count"
    )
    r = session.get(url)

    if r.status_code != requests.codes.OK:
        logging.info("Please contact developer to set corpus item count")

    return int(r.text.strip())


def get_request_session():
    session = requests.Session()
    token = get_github_token()
    session.headers["Authorization"] = f"token {token}"
    return session


def download_zip_file(url, pecha_path, session=None):
    if session:
        r = session.get(url, stream=True)
    else:
        r = requests.get(url, stream=True)

    if r.status_code != requests.codes.OK:
        return

    corpus_path = pecha_path.parent
    out_fn_zip = corpus_path / f"{pecha_path.name}.zip"
    with out_fn_zip.open("wb") as f:
        for chunk in r.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

    # unzip the file
    with zipfile.ZipFile(str(out_fn_zip), "r") as zip:
        zip.extractall(corpus_path)
        members = zip.namelist()

    out_fn_zip.unlink()
    unzipfile_path = corpus_path / members[0][:-1]
    shutil.move(str(unzipfile_path), str(pecha_path))


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
    corpus_output_path.mkdir(exist_ok=True, parents=True)
    session = get_request_session()
    corpus_catalog = get_corpus_catalog(corpus_name, session)
    corpus_items_count = get_corpus_items_count(corpus_name, session)
    logging.info(f"Downloading `{corpus_name}` corpus...")
    for corpus in tqdm(corpus_catalog, total=corpus_items_count):
        pecha_id, download_url, quality = corpus
        pecha_path = corpus_output_path / pecha_id
        if pecha_path.is_dir() and not replace:
            continue
        download_zip_file(download_url, pecha_path, session)


if __name__ == "__main__":
    download_corpus("literary_bo")
