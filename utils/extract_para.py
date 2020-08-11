import argparse
from pathlib import Path

from tqdm import tqdm


def extract_para(path):
    fn = path / f"{path.name}.opf" / "base.txt"
    paras = ""
    with fn.open() as f_read:
        for line in f_read.readlines():
            if len(line) > 300:
                line = line.replace("{", "")
                line = line.replace("}", "")
                paras += line
    return paras


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--path", type=str, help="directory path containing all the data")
    args = ap.parse_args()

    out_fn = Path("paragraphs.txt")
    for path in tqdm(list(Path(args.path).iterdir())):
        paras = extract_para(path)

        if paras:
            with out_fn.open("a") as f_append:
                f_append.write(paras)
