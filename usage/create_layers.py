import sys
sys.path.append('../')
# TODO: Above to be remove once the openpoti is uploaded to pypi

import argparse
from pathlib import Path
import shutil

from openpoti.openpoti import OpenPoti


def to_openpoti_format(ebook):
    ebook_name = ebook.name
    ebook_stem = ebook.stem

    conf = {
            'layers': f'layer_output/{ebook_stem}/{ebook_stem}.opf/layers/',
            'bases': f'layer_output/{ebook_stem}/{ebook_stem}.opf/',
            'input': 'input',
            'output': 'output'
        }

    print(ebook)
    existing = OpenPoti(conf)
    existing.new_poti(ebook_name)


if __name__ == "__main__":

    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--path", type=str, help="directory path containing all the data")
    args = ap.parse_args()

    for ebook in sorted([o for o in list(Path(args.path).iterdir()) if str(o).endswith('.txt')]):
        to_openpoti_format(ebook)

        #move all the ebook to output_layer/source
        source_ebook = f'{args.path}/{ebook.stem}.epub'
        ebook_export_path = Path(f'layer_output/{ebook.stem}/src')
        ebook_export_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(source_ebook, str(ebook_export_path))
        # if not ebook_export_path.is_dir():
        #     ebook_export_path.mkdir(parents=True, exist_ok=True)
        #     if not (ebook_export_path/f'{ebook.stem}.epub').is_file():
        #         shutil.copy(source_ebook, str(ebook_export_path))