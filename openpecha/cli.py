import logging
from pathlib import Path

import click
from git import Repo
from tqdm import tqdm

from openpecha.blupdate import PechaBaseUpdate
from openpecha.buda.openpecha_manager import OpenpechaManager
from openpecha.catalog import config as catalog_config
from openpecha.catalog.filter import is_text_good_quality
from openpecha.catalog.storage import GithubBucket
from openpecha.formatters import *
from openpecha.serializers import *

OP_PATH = Path.home() / ".openpecha"
config = {
    # Github
    "OP_CATALOG_URL": "https://raw.githubusercontent.com/OpenPoti/openpecha-catalog/master/data/catalog.csv",
    "OP_ORG": "https://github.com/OpenPecha",
    # Local
    "OP_DATA_PATH": (OP_PATH / "data").resolve(),
    "OP_CATALOG_PATH": (OP_PATH / "data" / "catalog.csv").resolve(),
    "CONFIG_PATH": (OP_PATH / "config").resolve(),
    "DATA_CONFIG_PATH": (OP_PATH / "config" / "data_config").resolve(),
}

ERROR = "[ERROR] {}"
INFO = "[INFO] {}"


def get_pecha_id(n):
    return f"P{int(n):06}"


@click.group()
def cli():
    pass


def create_config_dirs():
    config["OP_DATA_PATH"].mkdir(parents=True, exist_ok=True)
    config["CONFIG_PATH"].mkdir(parents=True, exist_ok=True)


def get_pecha(id, batch_path, layers):
    def _check_pecha(id=None, pechas=None, layer=None, pecha_list=None):
        if id not in pecha_list:
            if id in pechas:
                if layer:
                    if layer in pechas[id][-1].split("_"):
                        pecha_list.append(id)
                    else:
                        msg = f"{layer} layer is not found in {id}"
                        click.echo(ERROR.format(msg))
                else:
                    pecha_list.append(id)
            else:
                msg = f"{id} not found in OpenPecha catalog"
                click.echo(ERROR.format(msg))

    def _get_batch(batch_path):
        with Path(batch_path).open() as f:
            batch_ids = [line.strip() for line in f.readlines()]
        return batch_ids

    pecha_list = []

    # If filter by layers
    if layers:
        layers_name = [layer.strip() for layer in layers.split(",")]
        for layer in layers_name:
            batch_ids = None
            if id:
                _check_pecha(id=id, pechas=pechas, layer=layer, pecha_list=pecha_list)
            elif batch_path:
                if not batch_ids:
                    batch_ids = _get_batch(batch_path)
                for b_id in batch_ids:
                    _check_pecha(
                        id=b_id, pechas=pechas, layer=layer, pecha_list=pecha_list
                    )
            else:
                for p_id in pechas:
                    _check_pecha(
                        id=p_id, pechas=pechas, layer=layer, pecha_list=pecha_list
                    )
    else:
        if id:
            _check_pecha(id=id, pechas=pechas, pecha_list=pecha_list)
        elif batch_path:
            batch_ids = _get_batch(batch_path)
            for b_id in batch_ids:
                _check_pecha(id=b_id, pechas=pechas, pecha_list=pecha_list)
        else:
            for p_id in pechas:
                _check_pecha(id=p_id, pechas=pechas, pecha_list=pecha_list)

    return pecha_list


def get_default_branch(repo):
    if "main" in repo.heads:
        return "main"
    return "master"


def download_pecha(pecha_id, out_path=None):
    # clone the repo
    pecha_url = f"{config['OP_ORG']}/{pecha_id}.git"
    if out_path:
        out_path = Path(out_path)
        out_path.mkdir(exist_ok=True, parents=True)
        pecha_path = out_path / pecha_id
    else:
        pecha_path = config["OP_DATA_PATH"] / pecha_id

    if pecha_path.is_dir():  # if repo is already exits at local then try to pull
        repo = Repo(str(pecha_path))
        default_branch = get_default_branch(repo)
        repo.heads[default_branch].checkout()
        click.echo(INFO.format(f"Updating {pecha_id} ..."))
        repo.remotes.origin.pull()
    else:
        click.echo(INFO.format(f"Downloading {pecha_id} ..."))
        Repo.clone_from(pecha_url, str(pecha_path))
    return pecha_path


# Poti Download command
@cli.command()
@click.option("--number", "-n", help="Pecha number of pecha, for single pecha download")
@click.option(
    "--batch",
    "-b",
    help="path to text file containg list of names of \
                                     pecha in separate line. Poti batch download",
)
@click.option(
    "--filter",
    "-f",
    help="filter pecha by layer availability, specify \
                                     layer names in comma separated, eg: title,yigchung,..",
)
@click.option("--out", "-o", default="./pecha", help="directory to store all the pecha")
def download(**kwargs):
    """
    Command to download pecha.
    If id and batch options are not provided then it will download all the pecha.
    """
    pecha_id = get_pecha_id(kwargs["number"])

    # create config dirs
    create_config_dirs()

    # configure the data_path
    config["data"] = Path(kwargs["out"]).resolve()

    # get pecha
    # pechas = get_pecha(work_id, kwargs['batch'], kwargs['filter'])
    pechas = [pecha_id]

    # download the repo
    for pecha in tqdm(pechas):
        download_pecha(pecha, kwargs["out"])

    # save data_path in data_config
    config_path = config["DATA_CONFIG_PATH"]
    if not config_path.is_file():
        config_path.write_text(str(config["data"].resolve()))

    # print location of data
    msg = f"Downloaded {pecha_id} ... ok"
    click.echo(INFO.format(msg))


# OpenPecha Formatter
formatter_types = ["ocr", "hfml(default)", "tsadra"]


@cli.command()
@click.option(
    "--name", "-n", type=click.Choice(formatter_types), help="Type of formatter"
)
@click.option("--id", "-i", type=int, help="Id of the pecha")
@click.option("--output_path", "-o", help="output path to store opf pechas")
@click.argument("input_path")
def format(**kwargs):
    """
    Command to format pecha into opf
    """
    if kwargs["name"] == "ocr":
        formatter = GoogleOCRFormatter(kwargs["output_path"])
    elif kwargs["name"] == "tsadra":
        formatter = HFMLFormatter(kwargs["output_path"])
    else:
        formatter = HFMLFormatter(kwargs["output_path"])

    formatter.create_opf(kwargs["input_path"], kwargs["id"])


@cli.command()
@click.option("--cache-folder", "-c", help="path to the folder of the local cache")
@click.option("--idlist", "-l", help="comma-separated list of Openpecha IDs")
def pull_pechas(cache_folder, idlist):
    """
    Command to pull all the pechas in local cache
    """
    opm = None
    if cache_folder is not None:
        opm = OpenpechaManager(local_dir=cache_folder)
    else:
        opm = OpenpechaManager()
    if idlist is None:
        opm.fetch_all_pecha()
    else:
        opids = idlist.split(",")
        for opid in tqdm(opids, ascii=True, desc="Cloning or pulling the pecha"):
            opm.fetch_pecha(opid)


@cli.command()
@click.option("--cache-folder", "-c", help="path to the folder of the local cache")
@click.option("--store-uri", "-s", help="Fuseki URI", required=True)
@click.option(
    "--force",
    "-f",
    help="force upload even when commit match with triple store",
    is_flag=True,
)
@click.option(
    "--ldspdi-uri", "-u", help="lds-pdi URI", default="https://ldspdi.bdrc.io/"
)
@click.option("--idlist", "-l", help="comma-separated list of Openpecha IDs")
@click.option("--verbose", "-v", help="verbose", is_flag=True)
@click.option("--debug", "-d", help="debug", is_flag=True)
def cache_to_store(cache_folder, ldspdi_uri, store_uri, force, verbose, debug, idlist):
    """
    Update the cached version of synced commits
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    opm = None
    if cache_folder is not None:
        opm = OpenpechaManager(local_dir=cache_folder)
    else:
        opm = OpenpechaManager()
    opids = None
    if idlist is not None:
        opids = idlist.split(",")
    opm.sync_cache_to_store(store_uri, ldspdi_uri, force, opids)


export_types = ["hfml(default)", "epub"]


@cli.command()
@click.option(
    "--name", "-n", type=click.Choice(export_types), help="Type of export format"
)
@click.option("--opf_path", "-op")
@click.option("--output_path", "-o")
def export(**kwargs):
    """
    Command to export Pecha in epub
    """

    opf_path = kwargs["opf_path"]
    output_path = kwargs["output_path"]
    if not opf_path:
        opf_path = f'{config["OP_DATA_PATH"]}/{pecha_id}/{pecha_id}.opf'

    if kwargs["name"] == "epub":
        serializer = EpubSerializer(opf_path)
    else:
        serializer = HFMLSerializer(opf_path)
    serializer.serialize(kwargs["output_path"])


def _get_bucket(bucket_type, bucket_name, n):
    if bucket_type == "github":
        catalog_config.GITHUB_BUCKET_CONFIG["catalog"]["end"] = n
        return GithubBucket(bucket_name, config=catalog_config.GITHUB_BUCKET_CONFIG)


def _get_filter_strategy_caller(filter_strategy):
    if filter_strategy == "non_words_ratio":
        try:
            from bonltk.text_quality import non_words_ratio
        except Exception:
            msg = (
                "bonltk not installed. Install it with `pip install bonltk` "
                "or from https://github.com/10zinten/bonltk"
            )
            raise ImportError(msg)
        return non_words_ratio


def _save_text(text, output_path, parent_path, fn):
    pecha_path = Path(output_path) / parent_path
    pecha_path.mkdir(exist_ok=True)
    vol_path = pecha_path / fn
    vol_path.write_text(text)


@cli.command()
@click.option("--output_path", "-o", type=click.Path(exists=True), required=True)
@click.option("--bucket_type", "-bt", type=click.Choice(["github"]), default="github")
@click.option("--bucket_name", "-bn", type=str, default="OpenPecha")
@click.option(
    "--filter_strategy",
    "-fs",
    type=click.Choice(["non_words_ratio"]),
    default="non_words_ratio",
)
@click.option(
    "--threshold",
    "-th",
    type=float,
    default=0.8,
    help="Determines the quality of the text (1 being the highest and 0 being the lowest)",
)
@click.option("-n", type=int, default=1, help="number of pechas to download")
@click.option("--verbose", "-v", help="verbose", is_flag=True)
@click.option("--debug", "-d", help="debug", is_flag=True)
def corpus_download(
    output_path, bucket_type, bucket_name, filter_strategy, threshold, n, verbose, debug
):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)

    bucket = _get_bucket(bucket_type, bucket_name, n)
    filter_strategy_caller = _get_filter_strategy_caller(filter_strategy)
    for pecha_id, base in bucket.get_all_pechas_base():
        for vol_base, vol_fn in base:
            if is_text_good_quality(
                vol_base, strategy=filter_strategy_caller, threshold=threshold
            ):
                _save_text(vol_base, output_path, pecha_id, vol_fn)


@cli.command()
@click.argument("pecha_number")
@click.argument("pecha_path")
def update_layers(**kwargs):
    """
    Update all the layers when base has been updated.
    """
    pecha_id = get_pecha_id(kwargs["pecha_number"])
    src_pecha_path = download_pecha(pecha_id)

    click.echo(INFO.format(f"Updating base of {pecha_id} ..."))
    src_opf_path = src_pecha_path / f"{pecha_id}.opf"
    dst_opf_path = Path(kwargs["pecha_path"]) / f"{pecha_id}.opf"
    pecha = PechaBaseUpdate(src_opf_path, dst_opf_path)
    pecha.update()
