import logging
import shutil
import traceback
from pathlib import Path

import click
from tqdm import tqdm

import openpecha
from openpecha import config
from openpecha.alignment.tmx import create_opf as alignment
from openpecha.blupdate import PechaBaseUpdate
from openpecha.core.pecha import OpenPechaFS
from openpecha.corpus.quality import NonWordsCounter
from openpecha.formatters import GoogleVisionFormatter, HFMLFormatter
from openpecha.serializers import EpubSerializer, HFMLSerializer
from openpecha.utils import download_pecha as download_pecha_util

OP_PATH = config.BASE_PATH
config = {
    # Github
    "OP_CATALOG_URL": "https://raw.githubusercontent.com/OpenPoti/openpecha-catalog/master/data/catalog.csv",
    "OP_ORG": "https://github.com/OpenPecha",
    # Local
    "OP_DATA_PATH": (OP_PATH / "data").resolve(),
    "OP_PECHAS_PATH": config.PECHAS_PATH.resolve(),
    "OP_CATALOG_PATH": (OP_PATH / "data" / "catalog.csv").resolve(),
    "CONFIG_PATH": (OP_PATH / "config").resolve(),
    "DATA_CONFIG_PATH": (OP_PATH / "config" / "data_config").resolve(),
}

ERROR = "[ERROR] {}"
INFO = "[INFO] {}"


def get_pecha_id(n):
    return f"P{int(n):06}"


@click.group()
@click.version_option(version=openpecha.__version__)
def cli():
    pass


@cli.command()
@click.argument("pecha_id")
@click.option("--out", "-o", help="Directory to save the pecha")
@click.option("--branch", "-b", help="Which branch to download, default is `main`")
def download_pecha(**kwargs):
    """
    Download a single pecha.
    """
    pecha_id = kwargs["pecha_id"]
    output_path = kwargs["out"]
    branch = kwargs["branch"]

    click.echo(f"✨ Downloading {pecha_id}️...")

    try:
        pecha_path = download_pecha_util(pecha_id, out_path=output_path, branch=branch)
    except Exception as e:
        click.echo(f"❌ Failed to download {pecha_id}...x")
        click.echo(f"❌ {e}")
        return

    click.echo(f"✅ Download completed")
    click.echo(f"📖 Pecha saved at {pecha_path.resolve()}")


@cli.command()
@click.argument("batch_file_path")
@click.option("--out", "-o", help="Directory to save the pecha")
@click.option("--branch", "-b", help="Which branch to download, default is `main`")
def download_pecha_batch(**kwargs):
    """
    Download a batch of pechas.
    """
    batch_file_path = Path(kwargs["batch_file_path"])
    output_path = kwargs["out"]
    branch = kwargs["branch"]

    assert batch_file_path.is_file()

    # resolve outpout path
    output_path = output_path if output_path else (Path.cwd() / batch_file_path.stem)
    output_path = Path(output_path).resolve()
    output_path.mkdir(exist_ok=True, parents=True)

    click.echo(f"✨ Downloading  the batch {batch_file_path.name}...")

    for pecha_id in tqdm(batch_file_path.read_text().splitlines()):
        if not pecha_id:
            continue

        try:
            download_pecha_util(pecha_id, out_path=output_path, branch=branch)
        except Exception as e:
            click.echo(f"❌ Failed to download {pecha_id}...x")
            click.echo("❌ Error: {e}")
            continue

    click.echo(f"✅ Download completed")
    click.echo(f"📚 Batch saved at {output_path}")


# OpenPecha Formatter
formatter_types = ["ocr", "hfml(default)", "tsadra"]


@cli.command()
@click.option(
    "--name", "-n", type=click.Choice(formatter_types), help="Type of formatter"
)
@click.option("--id", "-i", type=int, help="Id of the pecha")
@click.option("--output_path", "-o", help="output path to store opf pechas")
@click.argument("input_path")
def import_text(**kwargs):
    """
    Import text from a file to OpenPecha format.
    """
    if kwargs["name"] == "ocr":
        formatter = GoogleVisionFormatter(kwargs["output_path"])
    elif kwargs["name"] == "tsadra":
        formatter = HFMLFormatter(kwargs["output_path"])
    else:
        formatter = HFMLFormatter(kwargs["output_path"])

    formatter.create_opf(kwargs["input_path"], kwargs["id"])


export_types = ["hfml(default)", "epub"]


@cli.command()
@click.option(
    "--name", "-n", type=click.Choice(export_types), help="Type of export format"
)
@click.option("--opf_path", "-op")
@click.option("--output_path", "-o")
def export_text(**kwargs):
    """
    Export text from OpenPecha format to a specified file format.
    """

    opf_path = kwargs["opf_path"]
    output_path = kwargs["output_path"]
    # if not opf_path:
    #     opf_path = f'{config["OP_PECHAS_PATH"]}/{pecha_id}/{pecha_id}.opf'

    if kwargs["name"] == "epub":
        serializer = EpubSerializer(opf_path)
    else:
        serializer = HFMLSerializer(opf_path)
    serializer.serialize(output_path)


@cli.command()
@click.argument("pecha_number")
@click.argument("pecha_path")
def update_layers(**kwargs):
    """
    Update all the layers when base has been updated.
    """
    pecha_id = get_pecha_id(kwargs["pecha_number"])
    src_pecha_path = download_pecha_util(pecha_id)

    click.echo(INFO.format(f"Updating base of {pecha_id} ..."))
    src_opf_path = src_pecha_path / f"{pecha_id}.opf"
    dst_opf_path = Path(kwargs["pecha_path"]) / f"{pecha_id}.opf"
    pecha = PechaBaseUpdate(src_opf_path, dst_opf_path)
    pecha.update()


def get_alignment_ids(path):
    path = Path(path)
    return [line for line in path.read_text().splitlines() if line]


alignment_import_types = ["tmx"]


@cli.command()
@click.argument("path")
@click.option("--verbose", "-v", help="verbose", is_flag=True)
@click.option("--debug", "-d", help="debug", is_flag=True)
@click.option(
    "--type",
    "-t",
    type=click.Choice(alignment_import_types),
    help="Type of alignment import format. Default is tmx",
)
@click.option(
    "--tm-path", "-tm", help="path to file containing OpenPecha alignment id's"
)
def import_alignment(**kwargs):
    """
    import existing alignment into OpenPecha
    """
    try:
        from openpecha.alignment.integrations.tx import OPATransifexProject
    except Exception:
        raise ImportError(
            "install with `pip install openpecha[tx]` for transifex dependencies"
        )

    if kwargs["debug"]:
        logging.basicConfig(level=logging.DEBUG)
    elif kwargs["verbose"]:
        logging.basicConfig(level=logging.INFO)
    logging.info("Creating OpenPecha alignment")
    alignment_path = alignment.create_alignment_from_tmx(tmx_path=Path(kwargs["path"]))

    added_tms_path = []
    try:
        logging.info(f"Alignment created at {alignment_path}")
        project = OPATransifexProject(org_slug="esukhia", alignment_path=alignment_path)
        project.create()
        project.import_translation()
        logging.info("Imported translation")
        logging.info("Adding TMs")
        added_tms_path = project.add_tm(
            alignment_ids=get_alignment_ids(kwargs["tm_path"])
        )
    except Exception as e:
        print(traceback.print_exc(), e)
        logging.info("Cleaning up")
        # shutil.rmtree(str(alignment_path))
    finally:
        if alignment_path.is_dir and added_tms_path:
            logging.info("Cleaning up")
            if alignment_path.is_dir():
                shutil.rmtree(str(alignment_path))
            for path in added_tms_path:
                shutil.rmtree(str(path))


@cli.command()
@click.argument("path")
@click.option("-t", "--title", help="title of the text")
@click.option(
    "--tm-path", "-tm", help="path to file containing OpenPecha alignment id's"
)
def new_translation(**kwargs):
    """
    prepare translation project in transifex
    """
    try:
        from openpecha.alignment.integrations.tx import OPATransifexProject
    except Exception:
        raise ImportError(
            "install with `pip install openpecha[tx]` for transifex dependencies"
        )

    alignment_path = alignment.create_alignment_from_source_text(
        text_path=Path(kwargs["path"])
    )
    project = OPATransifexProject(org_slug="esukhia", alignment_path=alignment_path)
    project.create()
    project.start_new_translation()
    project.add_tm(alignment_ids=get_alignment_ids(kwargs["tm_path"]))


@cli.command()
@click.argument("pecha_path")
@click.option("--save", "-s", help="save non-words counts", is_flag=True)
def qc(**kwargs):
    """
    check quality of pecha base text
    """
    pecha = OpenPechaFS(path=kwargs["pecha_path"])

    click.echo("Counting Non Words...")
    non_words_count = NonWordsCounter(empty=True)
    for base_name in pecha.components.keys():
        text = pecha.get_base(base_name)
        non_words_count += NonWordsCounter(text)

    if kwargs["save"]:
        pecha.meta.statistics["total_words"] = non_words_count.total_words
        pecha.meta.statistics["total_non_words"] = non_words_count.total_non_words
        pecha.meta.quality["non_words_ratio"] = non_words_count.non_word_ratio
        pecha.save_meta()
