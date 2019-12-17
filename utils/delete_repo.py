import argparse
import os
from pathlib import Path

from github import Github

g = Github(os.environ.get('GITHUB_TOKEN'))
org = g.get_organization('OpenPecha')

if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--prefix", type=str, help="prefix of repos to be deleted in bulk")
    args = ap.parse_args()

    for repo in org.get_repos():
        if repo.name.startswith(args.prefix):
            repo.delete()
            print(f'[INFO] {repo} is deleted.')