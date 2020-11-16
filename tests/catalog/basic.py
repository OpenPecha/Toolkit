import os

from openpecha.catalog.storage import GithubBucket

if __name__ == "__main__":

    GITHUB_BUCKET_CONFIG = {
        "catalog": {"start_id": 0, "end_id": 0},
        "token": os.environ.get("GITHUB_TOKEN"),
    }

    bucket = GithubBucket("OpenPecha", config=GITHUB_BUCKET_CONFIG)
    for pecha_id, base in bucket.get_all_pechas_base():
        print(pecha_id)
        for vol_base, vol_fn in base:
            print(vol_fn, vol_base)
