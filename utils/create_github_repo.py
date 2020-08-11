import argparse
import os
import shutil
from pathlib import Path

from git import Repo
from github import Github

g = Github(os.environ.get("GITHUB_TOKEN"))
org = g.get_organization("OpenPecha")


def populate_repo(repo_path, from_path):
    for o in from_path.iterdir():
        shutil.move(str(o), str(repo_path))
    from_path.rmdir()


def create_github_repo(path):
    repo = org.create_repo(path.name)
    repo.create_file("README.md", "add README.md", "", branch="master")
    return repo._ssh_url.value


def commit(repo, message):
    has_changed = False

    # add untrack files
    for file in repo.untracked_files:
        print(f"Added untracked file: {file}")
        if file:
            repo.git.add(file)
        if has_changed is False:
            has_changed = True

    # add modified files
    if repo.is_dirty() is True:
        for file in repo.git.diff(None, name_only=True).split("\n"):
            print(f"Added file: {file}")
            if file:
                repo.git.add(file)
            if has_changed is False:
                has_changed = True

    if has_changed is True:
        repo.git.commit("-m", message)
        repo.git.push("origin", "master")
        print("[INFO] Commited and Pushed ->", repo)


def create_repo_and_commit(path, message):
    if (path / ".git").is_dir():
        print(f"[INFO] updating repo: {path.name}")
        # update_repo(path)
        repo = Repo(path)
        commit(repo, message)
    else:
        print(f"[INFO] Cloning repo: {path.name}")
        backup_repo = path.parent / "repo_bake"
        path.rename(backup_repo)
        remote_repo_url = create_github_repo(path)
        repo = Repo.clone_from(remote_repo_url, path)
        populate_repo(path, backup_repo)
        commit(repo, message)


if __name__ == "__main__":

    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--path", type=str, help="directory path containing all the data")
    ap.add_argument("-m", type=str, help="git commit message")
    args = ap.parse_args()

    for path in Path(args.path).iterdir():
        create_repo_and_commit(path, args.m)
