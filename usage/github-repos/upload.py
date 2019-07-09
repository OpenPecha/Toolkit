import argparse
from pathlib import Path
import shutil

from github import Github
from git import Repo


g = Github("10zinten", "Ten9882231253")
org = g.get_organization('OpenPecha')

def update_repo(path):
    for o in path.iterdir():
        shutil.move(str(o), path.name)

def create_github_repo(path):
    repo = org.create_repo(path.name)
    repo.create_file('README.md', 'add README.md', '', branch='master')
    return repo._ssh_url.value


def commit(repo, message):
    has_changed = False

    for file in repo.untracked_files:
        print(f'Added untracked file: {file}')
        repo.git.add(file)
        if has_changed is False:
            has_changed = True

    # if repo.is_dirty() is True:
    #     for file in repo.git.diff(None, name_only=True).split('\n'):
    #         print(f'Added file: {file}')
    #         repo.git.add(file)
    #         if has_changed is False:
    #             has_changed = True
    
    if has_changed is True:
        repo.git.commit('-m', message)
    repo.git.push('origin', 'master')


def create_repo_and_commit(path, message):
    if Path(path.name).is_dir():
        print(f'[INFO] updating repo: {path.name}')
        update_repo(path)
        repo = Repo(path.name)
        commit(repo, message)
    else:
        # Path(path.name).mkdir()
        print(f'[INFO] Cloning repo: {path.name}')
        remote_repo_url = create_github_repo(path)
        repo =  Repo.clone_from(remote_repo_url, path.name)
        update_repo(path)
        commit(repo, message)


if __name__ == "__main__":

    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--path", type=str, help="directory path containing all the data")
    args = ap.parse_args()

    for path in Path(args.path).iterdir():
        if path.name in ['W1OP000001', 'W1OP000002', 'W1OP000005']:
            Repo.clone_from(f'git@github.com:OpenPecha/{path.name}.git', path.name)
            continue
        create_repo_and_commit(path, message='initial commit')
