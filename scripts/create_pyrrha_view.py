import csv
import os
from pathlib import Path

import botok

os.chdir("../../openpecha-user/opfs/P000100")

# paths
pecha_id = Path.cwd().name
base_path = Path.cwd() / f"{pecha_id}.opf" / "base"
assert base_path.is_dir()

# pyrrha format
cols_name = ["form", "lemma", "POS", "morph"]


def get_token_attrs(token):
    form = token.text_unaffixed
    lemma = token.lemma
    pos = token.pos

    # add tsek for failed `token.text_unaffixed`
    if pos:
        if not form.endswith("་"):
            form += "་"

    # add pos to PUNCT type
    if token.chunk_type == "PUNCT":
        form = token.text.strip()
        pos = token.chunk_type

    return form, lemma, pos


def save_to_pyrrha_format(tokens, output_fn: Path):
    with output_fn.open("w") as out_file:
        tsv_writer = csv.writer(out_file, delimiter="\t")
        tsv_writer.writerow(cols_name)
        for token in tokens:
            form, lemma, pos = get_token_attrs(token)
            tsv_writer.writerow([form, lemma, pos])


# tokenize with botok as save in Pyrrha format
wt = botok.WordTokenizer()
for base_fn in base_path.iterdir():
    tokens = wt.tokenize(base_fn.read_text())
    output_fn = Path.cwd() / f"{base_fn.stem}.tsv"
    save_to_pyrrha_format(tokens, output_fn)

# Create readme
readme_path = Path.cwd() / "README.md"
readme_content = f"Config\n----\n- Tokenizer: `botok-v{botok.vars.__version__}`"
readme_path.write_text(readme_content)
