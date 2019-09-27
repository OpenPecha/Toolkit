import csv
import requests
import zipfile
from io import BytesIO, StringIO
from pathlib import Path
import shutil

import click
from github import Github
from git import Repo
from tqdm import tqdm

from openpoti.serializemd import SerializeMd

OP_PATH = './.openpoti'
config = {
    # Github
    'OP_CATALOG_URL': 'https://raw.githubusercontent.com/OpenPoti/openpoti-catalog/master/data/catalog.csv',
    'OP_ORG': 'https://github.com/OpenPoti',

    # Local
    'OP_DATA_PATH': f'{OP_PATH}/data',
    'OP_CATALOG_PATH': f'{OP_PATH}/data/catalog.csv',
    'CONFIG_PATH': f'{OP_PATH}/config',
    'DATA_CONFIG_PATH': f'{OP_PATH}/config/data_config',
}


@click.group()
def cli():
    pass


def create_config_dirs():
    Path(config['OP_DATA_PATH']).mkdir(parents=True, exist_ok=True)
    Path(config['CONFIG_PATH']).mkdir(parents=True, exist_ok=True)


def get_poti_list():
    poti_list = []

    catalog_path = Path(config['OP_CATALOG_PATH'])
    if not catalog_path.is_file():
        # download the catalog
        r = requests.get(config['OP_CATALOG_URL'])
        catalog_path.write_text(r.content.decode('utf-8'))
    
    # parse the poti workid
    with catalog_path.open('r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if not row[0].startswith('W'): continue
            poti_list.append(row[0])

    return poti_list


def download_poti(poti, out):
    # clone the repo
    poti_url = f"{config['OP_ORG']}/{poti}.git"
    poti_path = Path(config['OP_DATA_PATH'])/poti
    if poti_path.is_dir(): # if repo is already exits at local then try to pull
        repo = Repo(str(poti_path))
        repo.remotes.origin.pull()
    else:
        Repo.clone_from(poti_url, str(poti_path))
    
    # Create duplicate base-text for editing
    base_text = poti_path/f'{poti}.opf'/'base.txt'
    out_dir = Path(out)
    if not out_dir.is_dir(): out_dir.mkdir()
    dup_base_text = Path(out)/f'{poti}.txt'
    shutil.copy(str(base_text), str(dup_base_text))


# Download openPoti
@cli.command()
@click.option('--out', '-o', default='./poti',
                            help='directory to store all the poti')
def download(**kwargs):
    # create config dirs
    create_config_dirs()

    # configure the data_path
    config['data'] = Path(kwargs['out'])

    # download the repo
    poti_list = get_poti_list()
    for poti in tqdm(poti_list[:2]):
        download_poti(poti, kwargs['out'])

    # save data_path in data_config
    config_path = Path(config['DATA_CONFIG_PATH'])
    if not config_path.is_file():
        config_path.write_text(str(config['data'].resolve()))

    # print location of data
    print('Poti saved at:', Path(kwargs['out']).resolve())


# Apply layer
layers_name = ['title', 'tsawa', 'yigchung', 'quotes', 'sapche']

@cli.command()
@click.option('--name', '-n', type=click.Choice(layers_name), \
                              help='name of a layer to be applied')
@click.option('--list', '-l', help='list of name of layers to applied, \
                          name of layers should be comma separated')
@click.argument('opf_path', type=click.Path(exists=True))
@click.argument('out', type=click.File('w'))
def layer(**kwargs):
    """
    Command to apply a single layer, multiple layers or all available layers (by default) and then export to markdown.\n
    Args:\n
        - OPF_PATH is the path to opf directory of poti\n
        - OUT is the filename to the write the result. Currently support only Markdown file.
    """
    serializer = SerializeMd(kwargs['opf_path'])
    if kwargs['name']:
        serializer.apply_layer(kwargs['name'])
    elif kwargs['list']:
        layers = kwargs['list'].split(',')
        serializer.layers = layers
        serializer.apply_layers()
    else:
        serializer.apply_layers()

    result = serializer.get_result()
    click.echo(result, file=kwargs['out'])