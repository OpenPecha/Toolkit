import csv
import requests
from pathlib import Path
import shutil

import click
from github import Github
from git import Repo
from tqdm import tqdm

from openpecha.serializemd import SerializeMd
from openpecha.blupdate import Blupdate
from openpecha.formatters import GoogleOCRFormatter
from openpecha.formatters import HFMLFormatter


OP_PATH = Path('./.openpecha')
config = {
    # Github
    'OP_CATALOG_URL': 'https://raw.githubusercontent.com/OpenPoti/openpecha-catalog/master/data/catalog.csv',
    'OP_ORG': 'https://github.com/OpenPoti',

    # Local
    'OP_DATA_PATH': (OP_PATH/'data').resolve(),
    'OP_CATALOG_PATH': (OP_PATH/'data'/'catalog.csv').resolve(),
    'CONFIG_PATH': (OP_PATH/'config').resolve(),
    'DATA_CONFIG_PATH': (OP_PATH/'config'/'data_config').resolve(),
}

ERROR = '[ERROR] {}'
INFO = '[INFO] {}'

def get_work_id(n):
    return f'W1OP{int(n):06}'

@click.group()
def cli():
    pass


def create_config_dirs():
    config['OP_DATA_PATH'].mkdir(parents=True, exist_ok=True)
    config['CONFIG_PATH'].mkdir(parents=True, exist_ok=True)


def get_poti(id, batch_path, layers):

    def _check_poti(id=None, potis=None, layer=None, poti_list=None):
        if id not in poti_list:
            if id in potis:
                if layer:
                    if layer in potis[id][-1].split('_'):
                        poti_list.append(id)
                    else:
                        msg = f'{layer} layer is not found in {id}'
                        click.echo(ERROR.format(msg))
                else:
                    poti_list.append(id)
            else:
                msg = f'{id} not found in OpenPecha catalog'
                click.echo(ERROR.format(msg))

    def _get_batch(batch_path):
        with Path(batch_path).open() as f:
            batch_ids = [line.strip() for line in f.readlines()]
        return batch_ids


    poti_list = []

    catalog_path = config['OP_CATALOG_PATH']
    if not catalog_path.is_file():
        # download the catalog
        r = requests.get(config['OP_CATALOG_URL'])
        catalog_path.write_text(r.content.decode('utf-8'))
    
    # Create hash map of poti
    with catalog_path.open('r') as f:
        reader = csv.reader(f, delimiter=',')
        potis = {poti[0]: poti[1:] for poti in reader if poti[0].startswith('W')}

    # If filter by layers
    if layers:
        layers_name = [l.strip() for l in layers.split(',')]
        for layer in layers_name:
            batch_ids = None
            if id:
                _check_poti(id=id, potis=potis, layer=layer, poti_list=poti_list)
            elif batch_path:
                if not batch_ids: batch_ids = _get_batch(batch_path)
                for b_id in batch_ids:
                    _check_poti(id=b_id, potis=potis, layer=layer, poti_list=poti_list)
            else:
                for p_id in potis:
                    _check_poti(id=p_id, potis=potis, layer=layer, poti_list=poti_list)
    else:
        if id:
            _check_poti(id=id, potis=potis, poti_list=poti_list)
        elif batch_path:
            batch_ids = _get_batch(batch_path)
            for b_id in batch_ids:
                _check_poti(id=b_id, potis=potis, poti_list=poti_list)
        else:
            for p_id in potis:
                _check_poti(id=p_id, potis=potis, poti_list=poti_list)

    return poti_list


def download_poti(poti, out):
    # clone the repo
    poti_url = f"{config['OP_ORG']}/{poti}.git"
    poti_path = config['OP_DATA_PATH']/poti
    if poti_path.is_dir(): # if repo is already exits at local then try to pull
        repo = Repo(str(poti_path))
        repo.heads['master'].checkout()
        repo.remotes.origin.pull()
    else:
        Repo.clone_from(poti_url, str(poti_path))
    
    # Create duplicate base-text for editing
    base_text = poti_path/f'{poti}.opf'/'base.txt'
    out_dir = Path(out)
    if not out_dir.is_dir(): out_dir.mkdir()
    dup_base_text = Path(out)/f'{poti}.txt'
    shutil.copy(str(base_text), str(dup_base_text))


# Poti Download command
@cli.command()
@click.option('--number', '-n', help='Work number of pecha, for single pecha download')
@click.option('--batch', '-b', help="path to text file containg list of names of \
                                     pecha in separate line. Poti batch download")
@click.option('--filter', '-f', help='filter pecha by layer availability, specify \
                                     layer names in comma separated, eg: title,yigchung,..')
@click.option('--out', '-o', default='./pecha',
                            help='directory to store all the pecha')
def download(**kwargs):
    '''
    Command to download poti.
    If id and batch options are not provided then it will download all the poti.
    '''
    work_id = get_work_id(kwargs['number'])

    # create config dirs
    create_config_dirs()

    # configure the data_path
    config['data'] = Path(kwargs['out']).resolve()

    # get poti
    potis = get_poti(work_id, kwargs['batch'], kwargs['filter'])

    # download the repo
    for poti in tqdm(potis):
        download_poti(poti, kwargs['out'])

    # save data_path in data_config
    config_path = config['DATA_CONFIG_PATH']
    if not config_path.is_file():
        config_path.write_text(str(config['data'].resolve()))

    # print location of data
    msg = f'Pecha saved at: {Path(kwargs["out"])}'
    click.echo(INFO.format(msg))


# Apply layer command
layers_name = ['title', 'tsawa', 'yigchung', 'quotes', 'sapche']

@cli.command()
@click.option('--name', '-n', type=click.Choice(layers_name), \
                              help='name of a layer to be applied')
@click.option('--list', '-l', help='list of name of layers to applied, \
                          name of layers should be comma separated')
@click.argument('work_number')
@click.argument('out', type=click.File('w'))
def layer(**kwargs):
    """
    Command to apply a single layer, multiple layers or all available layers (by default) and then export to markdown.\n
    Args:\n
        - WORK_NUMBER is the work number of the pecha, from which given layer will be applied\n
        - OUT is the filename to the write the result. Currently support only Markdown file.
    """
    work_id = get_work_id(kwargs['work_number'])
    opfpath = config["OP_DATA_PATH"]/work_id/f'{work_id}.opf'
    serializer = SerializeMd(opfpath)
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

    # logging
    msg = f'Output is save at: {kwargs["out"].name}'
    click.echo(INFO.format(msg))


def poti_list():
    return [poti.name for poti in config['OP_DATA_PATH'].iterdir()]

def get_data_path():
    return Path(config['DATA_CONFIG_PATH'].read_text().strip())


def check_edits(w_id):
    edit_path = get_data_path()
    data_path = config['OP_DATA_PATH']

    srcbl = (data_path/f'{w_id}'/f'{w_id}.opf'/'base.txt').read_text()
    dstbl = (edit_path/f'{w_id}.txt').read_text()

    return srcbl != dstbl, srcbl, dstbl


def setup_credential(repo):
    # setup authentication, if not done
    if not (config['CONFIG_PATH']/'credential').is_file():
        username = click.prompt('Github Username')
        password = click.prompt('Github Password', hide_input=True)
        # save credential
        (config['CONFIG_PATH']/'credential').write_text(f'{username},{password}')

    if not '@' in repo.remotes.origin.url:
        # get user credentials
        credential = (config['CONFIG_PATH']/'credential').read_text()
        username, password = [s.strip() for s in credential.split(',')]
        
        old_url = repo.remotes.origin.url.split('//')
        repo.remotes.origin.set_url(
            f'{old_url[0]}//{username}:{password}@{old_url[1]}'
        )
    
    return repo


def github_push(repo, branch_name, msg='made edits'):
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
            repo.git.push('--set-upstream', 'origin', current)
        except Exception as e:
            print(e)
            msg = f'Authentication failed: Try again later'
            click.echo(ERROR.format(msg))
            return False

    # finally checkout to master for apply layer on validated text
    repo.heads['master'].checkout()
    
    return True


def repo_reset(repo, branch_name):
    # remove edited branch
    repo.heads['master'].checkout()
    repo.delete_head(repo.heads[branch_name], force=True)

    # reset to the origin url
    url = repo.remotes.origin.url.split('@')
    protocol = url[0].split('//')[0]
    repo.remotes.origin.set_url(
            f'{protocol}//{url[1]}'
    )


# Update annotations command
@cli.command()
@click.argument('work_number')
def update(**kwargs):
    """
    Command to update the base text with your edits.
    """
    work_id = get_work_id(kwargs['work_number'])
    if work_id:
        if work_id in poti_list():
            repo_path = config["OP_DATA_PATH"]/work_id
            repo = Repo(str(repo_path))

            # if edited branch exists, then to check for changes in edited branch
            branch_name = 'edited'
            if branch_name in repo.heads:
                current = repo.heads[branch_name]
                current.checkout()

            is_changed, srcbl, dstbl = check_edits(work_id)
            if is_changed:
                msg = f'Updating {work_id} base text.'
                click.echo(INFO.format(msg))

                # Update layer annotations
                updater =  Blupdate(srcbl, dstbl)
                opfpath = repo_path/f'{work_id}.opf'
                updater.update_annotations(opfpath)

                # Update base-text
                src = get_data_path()/f'{work_id}.txt'
                dst = opfpath/'base.txt'
                shutil.copy(str(src), str(dst))

                # Create edited branch and push to Github
                status = github_push(repo, branch_name)

                # logging
                if status:
                    msg = f'Pecha edits {work_id} are uploaded for futher validation'
                    click.echo(INFO.format(msg))
                else:
                    repo_reset(repo, branch_name)
            else:
                msg = f'There are no changes in Pecha {work_id}'
                click.echo(ERROR.format(msg))
        else:
            msg = f'{work_id} does not exits, check the work-id'
            click.echo(ERROR.format(msg))


# OpenPecha Formatter
formatter_types = ['ocr', 'hfml']

@cli.command()
@click.option('--name', '-n', type=click.Choice(formatter_types),
                              help='Type of formatter')
@click.argument('input_path')
def format(**kwargs):
    '''
    Cammand to format pecha into opf
    '''
    if kwargs['name'] == 'ocr':
        formatter = GoogleOCRFormatter()
        formatter.new_poti(kwargs['input_path'])
    elif kwargs['name'] == 'hfml':
        formatter = HFMLFormatter()
        formatter.new_poti(kwargs['input_path'])