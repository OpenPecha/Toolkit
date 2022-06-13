import logging
import os
from pathlib import Path

from github import Github, GithubException
from tqdm import tqdm

from openpecha.corpus.download import (
    get_corpus_catalog,
    get_corpus_items_count,
    get_request_session,
)

logging.basicConfig(
    filename=f"{Path(__name__).stem}.log",
    format="%(asctime)s - %(levename)s - %(message)s",
)


def get_modified_content(url, session):
    r = session.get(url)
    return r.text + "\n"


def get_openpecha_org():
    token = os.environ["GITHUB_TOKEN"]
    org = os.environ["OPENPECHA_DATA_GITHUB_ORG"]
    g = Github(token)
    return g.get_organization(org)


def has_branch(branch_name, repo):
    try:
        repo.get_branch(branch_name)
        return True
    except GithubException:
        return False


def create_botok_view(repo, session):
    msg = "create botok view"
    if has_branch("botok", repo):
        return
    old_content = repo.get_contents(".github/workflows/create_botok_view.yml")
    new_content = get_modified_content(old_content.download_url, session)
    repo.update_file(old_content.path, msg, new_content, old_content.sha)


def main():
    org = get_openpecha_org()
    corpus_name = "literary_bo"
    session = get_request_session()
    corpus_catalog = get_corpus_catalog(corpus_name, session)
    corpus_items_count = get_corpus_items_count(corpus_name, session)
    for corpus in tqdm(corpus_catalog, total=corpus_items_count):
        pecha_id = corpus[0]
        pecha_repo = org.get_repo(pecha_id)
        try:
            create_botok_view(pecha_repo, session)
        except Exception as e:
            logging.error(f"[ERROR] {pecha_id} failed!")
            logging.exception(e)


if __name__ == "__main__":
    main()
