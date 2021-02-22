import os

GITHUB_BUCKET_CONFIG = {
    "catalog": {"start_id": 1, "end_id": 1},
    "token": os.environ.get("GITHUB_TOKEN"),
}
