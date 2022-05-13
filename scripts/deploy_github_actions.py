import argparse

import requests

from openpecha import config
from openpecha.github_utils import create_file


def get_pechas(args):
    url = f"https://raw.githubusercontent.com/OpenPecha/catalog/master/data/corpus/{args.corpus_name}.txt"
    r = requests.get(url)
    for pecha_id in r.text.split("\n"):
        if pecha_id:
            yield pecha_id


def get_actions(args):
    url = f"https://api.github.com/repos/OpenPecha/{args.actions_source_pecha}/contents/.github/workflows"
    r = requests.get(url)
    actions = {}
    for action in r.json():
        action_url = action["download_url"]
        r = requests.get(action_url)
        actions[action["name"]] = r.text
    return actions


def deploy_actions(pecha_ids, actions):
    for pecha_id in pecha_ids:
        for action_fn, action in actions.items():
            action_deploy_msg = action_fn.split(".")[0].replace("_", " ")
            action_path = ".github/workflows/" + action_fn
            try:
                create_file(pecha_id, action_path, action, action_deploy_msg)
            except Exception:
                try:
                    create_file(
                        pecha_id, action_path, action, action_deploy_msg, update=True
                    )
                except Exception:
                    print(
                        "[ERROR] Failed to deploy action: {} to {}".format(
                            action_fn, pecha_id
                        )
                    )
                    pass
        print("[INFO] Deployed actions for pecha {}".format(pecha_id))


def main():
    parser = argparse.ArgumentParser(description="Deploy GitHub Actions")
    parser.add_argument("corpus_name", type=str, help="corpus name")
    parser.add_argument(
        "--actions_source_pecha", type=str, help="pecha with actions", default="P000110"
    )

    args = parser.parse_args()

    pecha_ids = get_pechas(args)
    actions = get_actions(args)
    deploy_actions(pecha_ids, actions)


if __name__ == "__main__":
    exit(main())
