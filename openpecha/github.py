import os
from pathlib import Path

from github import Github
from git import Repo


g = Github(os.environ.get('GITHUB_TOKEN'))
org = g.get_organization('OpenPecha')

def create_github_repo(path):
    repo = org.create_repo(path.name)
    return repo._html_url.value


def commit(repo, message):
    has_changed = False

    # add untrack files
    for file in repo.untracked_files:
        if file: repo.git.add(file)
        if has_changed is False:
            has_changed = True

    # add modified files
    if repo.is_dirty() is True:
        for file in repo.git.diff(None, name_only=True).split('\n'):
            if file: repo.git.add(file)
            if has_changed is False:
                has_changed = True
    
    if has_changed is True:
        if not message:
            message = 'Initial commit'
        repo.git.commit('-m', message)
        repo.git.push('origin', 'master')


def create_local_repo(path, remote_url):
    if (path/'.git').is_dir():
        return Repo(path)
    else:
        repo = Repo.init(path)
        old_url = remote_url.split('//')
        usr, pw = os.environ['GH_USR'], os.environ['GH_PW']
        auth_remote_url = f'{old_url[0]}//{usr}:{pw}@{old_url[1]}'
        repo.create_remote('origin', auth_remote_url)
        return repo


def github_publish(path, message=None, type=None):
    path = Path(path)
    remote_repo_url = create_github_repo(path)
    local_repo = create_local_repo(path, remote_repo_url)
    commit(local_repo, message)