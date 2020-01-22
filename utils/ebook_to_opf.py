import argparse
from pathlib import Path
import os

from openpecha.github import github_publish

START_PECHA = 10

def format_ebooks(path):
    global START_PECHA
    ebook_path = path/'OEBPS'
    cmd = f'openpecha format -n tsadra -i {START_PECHA} {str(ebook_path)}'
    os.system(cmd)
    START_PECHA += 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input", "-i", type=str, help="directory path containing all the data")
    ap.add_argument("--output", "-o", type=str, help="directory path containing all the data")
    args = ap.parse_args()

    # format all the ebooks to opf
    print('[INFO] OPF Formating ...')
    for path in Path(args.input).iterdir():
        if path.suffix == '.epub': continue
        print(f'\t- formatting {path.name}')
        format_ebooks(path)

    # publish all the opfs to github
    print('[INFO] OpenPecha Publish ...')
    for path in Path(args.output).iterdir():
        print(f'\t- Publishing {path.name} ...')
        github_publish(path)