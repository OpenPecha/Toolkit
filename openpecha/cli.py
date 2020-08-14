import csv
import logging
import shutil
from pathlib import Path

import click
import requests
from git import Repo
from github import Github
from tqdm import tqdm

from openpecha.blupdate import Blupdate
from openpecha.buda.openpecha_manager import OpenpechaManager
from openpecha.formatters import *
from openpecha.serializers import *
from openpecha.serializers import EpubSerializer

OP_PATH = Path("./.openpecha")
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


def download_pecha(pecha, out):
    # clone the repo
    pecha_url = f"{config['OP_ORG']}/{pecha}.git"
    pecha_path = config["OP_DATA_PATH"] / pecha
    if pecha_path.is_dir():  # if repo is already exits at local then try to pull
        repo = Repo(str(pecha_path))
        repo.heads["master"].checkout()
        repo.remotes.origin.pull()
    else:
        Repo.clone_from(pecha_url, str(pecha_path))


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


# Apply layer command
layers_name = ["title", "tsawa", "yigchung", "quotes", "sapche"]


@cli.command()
@click.option(
    "--name", "-n", type=click.Choice(layers_name), help="name of a layer to be applied"
)
@click.option(
    "--list",
    "-l",
    help="list of name of layers to applied, \
                          name of layers should be comma separated",
)
@click.argument("work_number")
@click.argument("out", type=click.File("w"))
def layer(**kwargs):
    """
    Command to apply a single layer, multiple layers or all available layers (by default) and then export to markdown.\n
    Args:\n
        - WORK_NUMBER is the work number of the pecha, from which given layer will be applied\n
        - OUT is the filename to the write the result. Currently support only Markdown file.
    """
    work_id = get_pecha_id(kwargs["work_number"])
    opfpath = config["OP_DATA_PATH"] / work_id / f"{work_id}.opf"
    serializer = SerializeMd(opfpath)
    if kwargs["name"]:
        serializer.apply_layer(kwargs["name"])
    elif kwargs["list"]:
        layers = kwargs["list"].split(",")
        serializer.layers = layers
        serializer.apply_layers()
    else:
        serializer.apply_layers()

    result = serializer.get_result()
    click.echo(result, file=kwargs["out"])

    # logging
    msg = f'Output is save at: {kwargs["out"].name}'
    click.echo(INFO.format(msg))


def pecha_list():
    return [pecha.name for pecha in config["OP_DATA_PATH"].iterdir()]


def get_data_path():
    return Path(config["DATA_CONFIG_PATH"].read_text().strip())


def check_edits(w_id):
    edit_path = get_data_path()
    data_path = config["OP_DATA_PATH"]

    srcbl = (data_path / f"{w_id}" / f"{w_id}.opf" / "base.txt").read_text()
    dstbl = (edit_path / f"{w_id}.txt").read_text()

    return srcbl != dstbl, srcbl, dstbl


def setup_credential(repo):
    # setup authentication, if not done
    if not (config["CONFIG_PATH"] / "credential").is_file():
        username = click.prompt("Github Username")
        password = click.prompt("Github Password", hide_input=True)
        # save credential
        (config["CONFIG_PATH"] / "credential").write_text(f"{username},{password}")

    if "@" not in repo.remotes.origin.url:
        # get user credentials
        credential = (config["CONFIG_PATH"] / "credential").read_text()
        username, password = [s.strip() for s in credential.split(",")]

        old_url = repo.remotes.origin.url.split("//")
        repo.remotes.origin.set_url(f"{old_url[0]}//{username}:{password}@{old_url[1]}")

    return repo


def github_push(repo, branch_name, msg="made edits"):
    # credential
    repo = setup_credential(repo)

    # checkout to edited branch
    if branch_name in repo.heads:
        current = repo.heads[branch_name]
    else:
        current = repo.create_head(branch_name)
    current.checkout()

    # Add, commit and push the edited branch
    if repo.is_dirty():
        repo.git.add(A=True)
        repo.git.commit(m=msg)
        try:
            repo.git.push("--set-upstream", "origin", current)
        except Exception as e:
            print(e)
            msg = "Authentication failed: Try again later"
            click.echo(ERROR.format(msg))
            return False

    # finally checkout to master for apply layer on validated text
    repo.heads["master"].checkout()

    return True


def repo_reset(repo, branch_name):
    # remove edited branch
    repo.heads["master"].checkout()
    repo.delete_head(repo.heads[branch_name], force=True)

    # reset to the origin url
    url = repo.remotes.origin.url.split("@")
    protocol = url[0].split("//")[0]
    repo.remotes.origin.set_url(f"{protocol}//{url[1]}")


# Update annotations command
@cli.command()
@click.argument("work_number")
def update(**kwargs):
    """
    Command to update the base text with your edits.
    """
    work_id = get_pecha_id(kwargs["work_number"])
    if work_id:
        if work_id in pecha_list():
            repo_path = config["OP_DATA_PATH"] / work_id
            repo = Repo(str(repo_path))

            # if edited branch exists, then to check for changes in edited branch
            branch_name = "edited"
            if branch_name in repo.heads:
                current = repo.heads[branch_name]
                current.checkout()

            is_changed, srcbl, dstbl = check_edits(work_id)
            if is_changed:
                msg = f"Updating {work_id} base text."
                click.echo(INFO.format(msg))

                # Update layer annotations
                updater = Blupdate(srcbl, dstbl)
                opfpath = repo_path / f"{work_id}.opf"
                updater.update_annotations(opfpath)

                # Update base-text
                src = get_data_path() / f"{work_id}.txt"
                dst = opfpath / "base.txt"
                shutil.copy(str(src), str(dst))

                # Create edited branch and push to Github
                status = github_push(repo, branch_name)

                # logging
                if status:
                    msg = f"Pecha edits {work_id} are uploaded for futher validation"
                    click.echo(INFO.format(msg))
                else:
                    repo_reset(repo, branch_name)
            else:
                msg = f"There are no changes in Pecha {work_id}"
                click.echo(ERROR.format(msg))
        else:
            msg = f"{work_id} does not exits, check the work-id"
            click.echo(ERROR.format(msg))


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
@click.option("--text_id", "-ti", type=str, help="text id of text")
@click.option("--vol_number", "-vn", type=int, help="vol number")
@click.argument("pecha_num")
def edit(**kwargs):
    """
    Command to export Pecha for editing work
    """
    pecha_id = get_pecha_id(kwargs["pecha_num"])
    opf_path = f'{config["OP_DATA_PATH"]}/{pecha_id}/{pecha_id}.opf'

    if kwargs["text_id"]:
        serializer = SerializeHFML(opf_path, text_id=kwargs["text_id"])
        out_fn = f'{pecha_id}-{kwargs["text_id"]}.txt'
    elif kwargs["vol_number"]:
        vol_id = f'v{kwargs["vol_number"]:03}'
        serializer = SerializeHFML(opf_path, vol_id=vol_id)
        out_fn = f"{pecha_id}-{vol_id}.txt"
    else:
        serializer = SerializeHFML(opf_path)
        out_fn = f"{pecha_id}-v001.txt"

    serializer.apply_layers()

    result = serializer.get_result()
    click.echo(result, file=open(out_fn, "w"))

    # logging
    msg = f"Output is save at: {out_fn}"
    click.echo(INFO.format(msg))


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
        serializer = SerializeHFML(opf_path)
    serializer.serialize(kwargs["output_path"])
