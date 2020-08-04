import argparse
import shutil
from pathlib import Path


def get_vol_id(path):
    vol_num = int(path.stem[1:])
    return f"v{vol_num:03}"


def rename_in_base(opf_path):
    base_path = opf_path / "base"
    for fn in base_path.iterdir():
        target_fn = base_path / f"{get_vol_id(fn)}.txt"
        fn.rename(target_fn)


def rename_in_layer(opf_path):
    layer_path = opf_path / "layers"
    for vol_dir in layer_path.iterdir():
        target_vol_dir = layer_path / get_vol_id(vol_dir)
        shutil.move(str(vol_dir), str(target_vol_dir))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument(
        "--path", "-p", type=str, help="directory path containing all the data"
    )
    args = ap.parse_args()

    pecha_path = Path(args.path)
    pecha_opf = pecha_path / f"{pecha_path.name}.opf"
    rename_in_base(pecha_opf)
    rename_in_layer(pecha_opf)
