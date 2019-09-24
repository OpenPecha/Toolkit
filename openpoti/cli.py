'''
TODO:
1. Download catalog.csv
2. Download all the OpenPotis
3. poti layer -n <layer-name> -l <layer_01, layer_02, ...> -a -o <path to opf file>
'''
import csv
import requests
import zipfile
from io import BytesIO, StringIO
from pathlib import Path

import click
from tqdm import tqdm

from openpoti.serializemd import SerializeMd


config = {
    'CATALOG_URL': 'https://raw.githubusercontent.com/OpenPoti/openpoti-catalog/master/data/catalog.csv',
    'OpenPotiRepo': 'https://github.com/OpenPoti/',
    'CONFIG_PATH': './.openpoti/config/data_config'
}


@click.group()
def cli():
    pass


def get_poti_list():
    poti_list = []

    # download the catalog
    r = requests.get(config['CATALOG_URL'])
    f = StringIO(r.content.decode('utf-8'))
    
    # parse the poti workid
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        if not row[0].startswith('W'): continue
        poti_list.append(row[0])

    return poti_list


def download_poti(poti):
    poti_url = f'https://github.com/OpenPoti/{poti}/archive/master.zip'

    # download the poti
    r = requests.get(poti_url)
    z = zipfile.ZipFile(BytesIO(r.content))
    z.extractall(config['data'])

    # rename the poti
    target = config['data']/poti
    if not target.is_dir():
        source = config['data']/f'{poti}-master'
        source.replace(target)

    #TODO: updating the poti


# Download openPoti
@cli.command()
@click.option('--save_dir', default='./.openpoti/data')
def download(save_dir):
    # configure the data_path
    config['data'] = Path(save_dir)

    # download the repo
    poti_list = get_poti_list()
    for poti in tqdm(poti_list[0:1]):
        download_poti(poti)

    # save data_path in data_config
    config_path = Path(config['CONFIG_PATH'])
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(str(config['data'].resolve()))


# Apply layer
@cli.command()
@click.argument("opf_path", type=click.Path(exists=True))
@click.option('--name', '-n', help='name of a layer to be applied')
@click.option('--list', '-l', help='list of name of layers to applied, \
                          name of layers should be comma separated')
def layer(**kwargs):
    print(kwargs['opf_path'])
    print(kwargs['name'])
    print(kwargs['list'])