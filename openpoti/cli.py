import csv
import requests
from pathlib import Path
import shutil

import click
from github import Github
from git import Repo
from tqdm import tqdm

from openpoti.serializemd import SerializeMd
from openpoti.blupdate import Blupdate


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

ERROR = '[ERROR] {}'
INFO = '[INFO] {}'


@click.group()
def cli():
    pass


def create_config_dirs():
    Path(config['OP_DATA_PATH']).mkdir(parents=True, exist_ok=True)
    Path(config['CONFIG_PATH']).mkdir(parents=True, exist_ok=True)


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
                msg = f'{id} not found in OpenPoti catalog'
                click.echo(ERROR.format(msg))

    def _get_batch(batch_path):
        with Path(batch_path).open() as f:
            batch_ids = [line.strip() for line in f.readlines()]
        return batch_ids


    poti_list = []

    catalog_path = Path(config['OP_CATALOG_PATH'])
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
    poti_path = Path(config['OP_DATA_PATH'])/poti
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
@click.option('--id', '-i', help='Work ID of poti, for single poti download')
@click.option('--batch', '-b', help="path to text file containg list of names of \
                                     poti in separate line. Poti batch download")
@click.option('--filter', '-f', help='filter poti by layer availability, specify \
                                     layer names in comma separated, eg: title,yigchung,..')
@click.option('--out', '-o', default='./poti',
                            help='directory to store all the poti')
def download(**kwargs):
    '''
    Command to download poti.
    If id and batch options are not provided then it will download all the poti.
    '''

    # create config dirs
    create_config_dirs()

    # configure the data_path
    config['data'] = Path(kwargs['out'])

    # get poti
    potis = get_poti(kwargs['id'], kwargs['batch'], kwargs['filter'])

    # download the repo
    for poti in tqdm(potis):
        download_poti(poti, kwargs['out'])

    # save data_path in data_config
    config_path = Path(config['DATA_CONFIG_PATH'])
    if not config_path.is_file():
        config_path.write_text(str(config['data'].resolve()))

    # print location of data
    msg = f'Poti saved at: {Path(kwargs["out"])}'
    click.echo(INFO.format(msg))


# Apply layer command
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

    # logging
    msg = f'Output is save at: {kwargs["out"]}'
    click.echo(INFO.format(msg))


def poti_list():
    return [poti.name for poti in Path(config['OP_DATA_PATH']).iterdir()]

def get_data_path():
    return Path(Path(config['DATA_CONFIG_PATH']).read_text().strip())


def check_edits(w_id):
    edit_path = get_data_path()
    data_path = Path(config['OP_DATA_PATH'])

    srcbl = (data_path/f'{w_id}'/f'{w_id}.opf'/'base.txt').read_text()
    dstbl = (edit_path/f'{w_id}.txt').read_text()

    return srcbl != dstbl, srcbl, dstbl


def github_push(repo, branch_name, msg='made edits'):
    # setup authentication, if not done
    if not '@' in repo.remotes.origin.url:
        
        username = click.prompt('Github Username')
        password = click.prompt('Github Password', hide_input=True)

        old_url = repo.remotes.origin.url.split('//')
        repo.remotes.origin.set_url(
            f'{old_url[0]}//{username}:{password}@{old_url[1]}'
        )

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
        except:
            msg = f'Authentication failed: Incorrect Username or Password'
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
@click.option('--id', '-i', help='Work ID of poti to be updated')
def update(**kwargs):
    """
    Command to update the annotations, must be run making edits to base-text.
    """
    if kwargs['id']:
        if kwargs['id'] in poti_list():
            repo_path = Path(f'{config["OP_DATA_PATH"]}')/f'{kwargs["id"]}'
            repo = Repo(str(repo_path))

            # if edited branch exists, then to check for changes in edited branch
            branch_name = 'edited'
            if branch_name in repo.heads:
                current = repo.heads[branch_name]
                current.checkout()

            is_changed, srcbl, dstbl = check_edits(kwargs['id'])
            if is_changed:
                msg = f'Updating annotations of Poti {kwargs["id"]}'
                click.echo(INFO.format(msg))

                # Update layer annotations
                updater =  Blupdate(srcbl, dstbl)
                opfpath = repo_path/f'{kwargs["id"]}.opf'
                updater.update_annotations(opfpath)

                # Update base-text
                src = get_data_path()/f'{kwargs["id"]}.txt'
                dst = opfpath/'base.txt'
                shutil.copy(str(src), str(dst))

                # Create edited branch and push to Github
                status = github_push(repo, branch_name)

                # logging
                if status:
                    msg = f'Poti {kwargs["id"]} is uploaded for futher validation'
                    click.echo(INFO.format(msg))
                else:
                    repo_reset(repo, branch_name)
            else:
                msg = f'There is not changes in Poti {kwargs["id"]}'
                click.echo(ERROR.format(msg))
        else:
            msg = f'{kwargs["id"]} does not exits, check the work id'
            click.echo(ERROR.format(msg))