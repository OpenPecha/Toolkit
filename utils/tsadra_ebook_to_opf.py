import argparse
import csv
import json
import os
from pathlib import Path

import yaml

from openpecha.github_utils import github_publish

START_PECHA = 10
catalog_data_path = Path("../openpoti-catalog/data/")
web_meta_path = (
    catalog_data_path / "website_metadata.json"
)  # save metadata in .opf/meta.yml
ebook_meta_path = (
    catalog_data_path / "ebook_metadata.csv"
)  # replace ID with new Pecha ID

# load the catalog data
web_meta = json.load(web_meta_path.open())
ebook_meta = csv.reader(ebook_meta_path.open())
ebook_meta_updated = [["ID", "Book Title", "Vol Numner", "Book Author", "Filename"]]


def format_ebooks(path):
    global START_PECHA
    ebook_path = path / "OEBPS"
    cmd = f"openpecha format -n tsadra -i {START_PECHA} {str(ebook_path)}"
    os.system(cmd)
    pecha_id = f"P{START_PECHA:06}"
    if not Path(f"./opfs/{pecha_id}/{pecha_id}.opf/meta.yml").is_file():
        raise Exception
    START_PECHA += 1


def create_readme(metadata, path):
    result = ""
    web_metadata = metadata["web_metadata"]
    # add title
    title = web_metadata["title"]
    result += f"## Title\n\t- {title['bo']}\n\t- {title['en']}\n\n"

    # add author
    author = web_metadata["author"]
    result += f"## Author\n\t- {author['bo']}\n\t- {author['en']}\n\n"

    readme_fn = path / "README.md"
    readme_fn.write_text(result)


def create_meta_fn(path):
    # populate web_metadata in opf meta.yml
    opf_meta_fn = path / f"{path.name}.opf" / "meta.yml"
    opf_meta = yaml.safe_load(opf_meta_fn.open())
    sku = opf_meta["ebook_metadata"]["sku"]
    for o in web_meta:
        if o["sku"] == sku:
            opf_meta["web_metadata"] = o
            yaml.dump(
                opf_meta,
                opf_meta_fn.open("w"),
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
            create_readme(opf_meta, path)
            break

    for row in ebook_meta:
        if row[-1] == sku:
            row[0] = path.name
            ebook_meta_updated.append(row)
            break


if __name__ == "__main__":
    # ap = argparse.ArgumentParser(add_help=False)
    # ap.add_argument("--input", "-i", type=str, help="path to tsadra ebooks")
    # ap.add_argument("--output", "-o", type=str, help="path to opfs")
    # args = ap.parse_args()

    input = "./bo_crawler/bo_crawler/data/tsadra/data/ebooks/"
    output = "./opfs"

    errors = ""
    errors_fn = Path("errors.txt")

    # format all the ebooks to opf
    print("[INFO] OPF Formating ...")
    for path in Path(input).iterdir():
        if path.suffix == ".epub":
            continue
        print(f"\t- formatting {path.name}")
        try:
            format_ebooks(path)
        except Exception:
            errors += path.name + "\n"

    # publish all the opfs to github
    print("[INFO] OpenPecha Publish ...")
    for path in Path(output).iterdir():
        try:
            create_meta_fn(path)
        except Exception:
            errors += path.name + "\n"
        # print(f'\t- Publishing {path.name} ...')
        # github_publish(path)

    errors_fn.write_text(errors)

    # save ebook_metadata
    with ebook_meta_path.open("w") as f:
        csv_writer = csv.writer(f, delimiter=",")
        for row in ebook_meta_updated:
            csv_writer.writerows(row)
