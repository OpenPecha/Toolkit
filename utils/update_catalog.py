"""Script to update the pecha mssing in catalog and sort the catalog."""

import argparse
import os
from pathlib import Path

import requests
import yaml
from github import Github

g = Github(os.environ.get("GITHUB_TOKEN"))
org = g.get_organization("OpenPecha")


def to_csv_format(rows, cols_name):
    """Return csv formated data."""
    data = cols_name + rows
    lines = [",".join([o for o in line]) for line in data]
    return "\n".join(lines)


def get_file_content(url, in_bytes=False):
    """Download file on given `url` and returns in bytes or text with `in_bytes`."""
    r = requests.get(url)
    if r.status_code != 200:
        return
    content = r.content
    if in_bytes:
        return content
    return content.decode("utf-8").strip()


def sort_catalog(data):
    """Sort catalog base on pecha number order."""
    return sorted(data, key=lambda x: x[0])


def get_catalog():
    """Return sorted openpecha catalog."""
    catalog_csv_url = (
        "https://github.com/OpenPecha/openpecha-catalog/raw/master/data/catalog.csv"
    )
    lines = get_file_content(catalog_csv_url).split("\n")
    catalog_data = [line.split(",") for line in lines]
    cols_name = catalog_data.pop(0)
    sorted_catalog_data = sort_catalog(catalog_data)
    return cols_name, sorted_catalog_data


def to_pecha_id_link(pecha_id):
    """Return pecha_id_link for `pecha_id`."""
    return f"[{pecha_id}](https://github.com/OpenPecha/{pecha_id}"


def get_metadata(pecha_id):
    """Return metadata in tuple for given `pecha_id."""
    metadata_url = (
        f"https://github.com/OpenPecha/{pecha_id}/raw/master/{pecha_id}.opf/meta.yml"
    )
    content = get_file_content(metadata_url, in_bytes=True)
    if not content:
        return
    metadata_dict = yaml.safe_load(content)
    csv_row = [
        to_pecha_id_link(pecha_id),
        metadata_dict["source_metadata"]["title"],
        "",
        "",
        metadata_dict["source_metadata"]["id"],
    ]
    return csv_row


def _pecha_id(link):
    """Return pecha number from markup hyperlink id."""
    pecha_id = link[1:8]
    return pecha_id, int(pecha_id[1:])


def update_catalog(start):
    """Update catalog with missing pecha."""
    cols_name, catalog_data = get_catalog()
    missing_row = []
    for i, pecha_row in enumerate(catalog_data, start):
        pecha_id, pecha_num = _pecha_id(pecha_row[0])
        if pecha_num == i:
            continue
        pecha_metadata = get_metadata(pecha_id)
        if pecha_metadata:
            missing_row.append(pecha_metadata)
    updated_catalog = catalog_data + missing_row
    updated_catalog = sort_catalog(update_catalog)
    return to_csv_format(update_catalog, cols_name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--start", "-s", type=int, help="start pecha number")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    output_fn = Path("catalog.csv")
    cols_name, catalog_data = get_catalog()
    if args.debug:
        print(to_csv_format(catalog_data, cols_name))
    output_fn.write_text(update_catalog(args.start))
