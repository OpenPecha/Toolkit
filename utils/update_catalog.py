"""Script to update the pecha mssing in catalog and sort the catalog."""

import argparse
import os
from pathlib import Path

import requests
import yaml
from github import Github


def to_csv_format(rows, cols_name):
    """Return csv formated data."""
    data = [cols_name] + rows
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
    catalog_csv_url = "https://raw.githubusercontent.com/OpenPecha/openpecha-catalog/master/data/catalog.csv"
    lines = get_file_content(catalog_csv_url).split("\n")
    catalog_data = [line.split(",") for line in lines]
    cols_name = catalog_data.pop(0)
    sorted_catalog_data = sort_catalog(catalog_data)
    return cols_name, sorted_catalog_data


def to_pecha_id_link(pecha_id):
    """Return pecha_id_link for `pecha_id`."""
    return f"[{pecha_id}](https://github.com/OpenPecha/{pecha_id})"


def get_pecha_metadata(pecha_id):
    """Return metadata in tuple for given `pecha_id."""
    metadata_url = f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/meta.yml"
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


def get_pecha_num_list(pechas):
    """Extract all the pecha numbers from `catalog_data.

    Args:
        pechas (list): list of pecha metatdata in list.

    Returns:
        list: list of pecha numbers.
    """
    return [int(pecha[0][2:8]) for pecha in pechas]


def update_catalog(start):
    """Update the catalog with missing pecha.

    Args:
        start (int): starting pecha number.

    Returns:
        str: updated catalog data in csv format.
    """
    cols_name, pechas = get_catalog()
    pecha_nums = get_pecha_num_list(pechas)
    missing_pechas = []
    for num in range(start, max(pecha_nums) + 1):
        if num in pecha_nums:
            continue
        pecha_metadata = get_pecha_metadata(f"P{num:06}")
        if pecha_metadata:
            print(f"[INFO] adding {pecha_metadata[0][1:8]}")
            missing_pechas.append(pecha_metadata)
    updated_catalog = pechas + missing_pechas
    updated_catalog = sort_catalog(updated_catalog)
    return to_csv_format(updated_catalog, cols_name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--start", "-s", type=int, help="start pecha number")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    output_fn = Path("resources/works/catalog.csv")
    cols_name, catalog_data = get_catalog()
    if args.debug:
        print(to_csv_format(catalog_data, cols_name))
    output_fn.write_text(update_catalog(args.start))
