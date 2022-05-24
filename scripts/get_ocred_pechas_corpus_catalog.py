import multiprocessing

import requests
import yaml

from openpecha.core.metadata import InitialCreationType, PechaMetadata
from openpecha.corpus.download import get_corpus_catalog, get_request_session


def _fix_old_metadata_attrs_name(metadata: str) -> str:
    metadata = metadata.replace("created_at", "imported")
    metadata = metadata.replace("last_modified_at", "last_modified")
    return metadata


def get_pecha_metadata(pecha_id: str) -> PechaMetadata:
    url = f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/meta.yml"
    session = get_request_session()
    r = session.get(url)

    if r.status_code != requests.codes.OK:
        print(f"metadata not found for pecha `{pecha_id}`")

    raw_metadata = _fix_old_metadata_attrs_name(r.text)
    metadata_dict = yaml.safe_load(raw_metadata)
    try:
        metadata = PechaMetadata.parse_obj(metadata_dict)
    except Exception:
        metadata = PechaMetadata(initial_creation_type=InitialCreationType.input)
    return metadata


def is_ocred_pecha(pecha_id: str):
    print(f"[INFO] checking {pecha_id}...")
    metadata = get_pecha_metadata(pecha_id)
    return metadata.initial_creation_type == InitialCreationType.ocr


def main():
    corpus_name = "literary_bo"
    session = get_request_session()
    corpus_catalog = get_corpus_catalog(corpus_name, session)
    pecha_ids = [row[0] for row in corpus_catalog]

    print("Finding ocred pecha...")
    with multiprocessing.Pool() as pool:
        check_ocred_pecha_ids = pool.map(is_ocred_pecha, pecha_ids)

    print(check_ocred_pecha_ids)
    for pecha_id, is_ocred in zip(pecha_ids, check_ocred_pecha_ids):
        if is_ocred:
            print(pecha_id)


if __name__ == "__main__":
    main()
