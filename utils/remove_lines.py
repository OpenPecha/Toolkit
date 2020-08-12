import argparse
from pathlib import Path

import yaml


def get_pg_layer(path):
    pecha_path = Path(path)
    pecha_id = pecha_path.name
    layer_path = pecha_path / f"{pecha_id}.opf" / "layers"
    for vol_path in layer_path.iterdir():
        print(f"[INFO] Processing {vol_path} ...")
        pg_fn = vol_path / "pagination.yml"
        yield pg_fn


def remove_lines(fn):
    ann = yaml.safe_load(fn.open())
    pg_ann = []
    for a in ann["content"]:
        if a["type"] == "page":
            pg_ann.append(a)
    ann["content"] = pg_ann
    yaml.dump(ann, fn.open("w"), default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument(
        "--path", "-p", type=str, help="directory path containing all the data"
    )
    args = ap.parse_args()

    for pg_fn in get_pg_layer(args.path):
        remove_lines(pg_fn)
