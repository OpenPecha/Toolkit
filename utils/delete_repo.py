import argparse
import datetime
import os
from pathlib import Path

from github import Github

g = Github(os.environ.get("GITHUB_TOKEN"))
org = g.get_organization("OpenPecha")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument(
        "--start",
        "-s",
        type=int,
        help="All pecha number greater than specified will be deleted",
    )
    args = ap.parse_args()

    delete_from_date = datetime.datetime(2020, 3, 23, 15, 0, 4)

    for repo in org.get_repos("all"):
        if repo.name.startswith(args.prefix):
            if args.start:
                repo_num = int(repo.name[len(args.prefix) :])
                if repo_num >= args.start:
                    repo.delete()
                    print(f"[INFO] {repo} is deleted.")
            else:
                if repo.created_at > delete_from_date:
                    repo.delete()
                    print(
                        f"[INFO] Deleting {repo.name} created at {str(repo.created_at)}"
                    )
