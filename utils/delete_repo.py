import argparse
import os
from pathlib import Path

from github import Github

g = Github(os.environ.get('GITHUB_TOKEN'))
org = g.get_organization('OpenPecha')
    

if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--prefix", "-p", type=str, help="prefix of repos to be deleted in bulk")
    ap.add_argument("--start", "-s", type=int, help="All pecha number greater than specified will be deleted")
    args = ap.parse_args()

    for repo in org.get_repos('all'):
        if repo.name.startswith(args.prefix):
            repo_num = int(repo.name[len(args.prefix):])
            if repo_num >= args.start:
                repo.delete()
                print(f'[INFO] {repo} is deleted.')