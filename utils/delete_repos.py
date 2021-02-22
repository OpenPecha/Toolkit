import argparse
import datetime
import os
from pathlib import Path

from github import Github

g = Github(os.environ.get("GITHUB_TOKEN"))
org = g.get_organization("OpenPecha")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--prefix", "-p", type=str, default="P", help="Repo prefix")
    ap.add_argument("--start", "-s", type=int, help="Start pecha number")
    ap.add_argument("--end", "-e", type=int, help="End pecha number")
    args = ap.parse_args()

    delete_from_date = datetime.datetime(2020, 3, 23, 15, 0, 4)

    if args.start and args.end is None:
        repo_name = f"{args.prefix}{args.start:06}"
        repo = org.get_repo(repo_name)
        repo.delete()
        print(f"[INFO] {repo_name} deleted")
    elif args.start and args.end:
        for repo in org.get_repos("all"):
            if repo.name.startswith(args.prefix):
                repo_num = int(repo.name[len(args.prefix) :])
                if args.start <= repo_num >= args.end:
                    repo.delete()
                    print(f"[INFO] {repo} deleted.")

            # else:
            #     if repo.created_at > delete_from_date:
            #         repo.delete()
            #         print(
            #             f"[INFO] Deleting {repo.name} created at {str(repo.created_at)}"
            #         )
