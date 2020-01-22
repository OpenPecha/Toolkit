import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input", type=str, help="directory path containing all the data")
    args = ap.parse_args()

    for op_path in Path(args.input).iterdir():
        op = op_path.name
        layers_path = op_path/f'{op}.opf'/'layers'
        for dmp_layer in layers_path.rglob('*.layer'):
            dmp_layer.unlink()

    
if __name__ == "__main__":
    main()