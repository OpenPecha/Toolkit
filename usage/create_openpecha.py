import argparse
import shutil
from pathlib import Path

from tqdm import tqdm

from openpecha.formatters import TsadraFormatter


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input", type=str, help="directory path containing all the data")
    ap.add_argument("--output", type=str, help="Path to export all the openpecha")
    args = ap.parse_args()
    formatter = TsadraFormatter(output_path=args.output)
    for m_text_file in tqdm(
        [o for o in list(Path(args.input).iterdir()) if str(o).endswith(".txt")]
    ):
        formatter.new_poti(m_text_file)

        # move all the ebook to output_layer/source
        # source_ebook = f'{args.path}/{m_text_file.stem}.epub'
        # ebook_export_path = Path(f'layer_output/{m_text_file.stem}/src')
        # ebook_export_path.mkdir(parents=True, exist_ok=True)
        # shutil.copy(source_ebook, str(ebook_export_path))


if __name__ == "__main__":
    main()
