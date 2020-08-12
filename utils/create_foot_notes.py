import os
from collections import defaultdict
from pathlib import Path

import yaml

from openpecha.serializers import SerializeFootNote

error_logs_fn = Path("./error_logs") / Path(__file__).stem
if error_logs_fn.is_file():
    error_logs_fn.unlink()


def to_bo_pagination(text):
    def index_to_bo(index):
        chars = list(index)
        result = ""
        for c in chars:
            if c.isdigit():
                result += bo_num[int(c)]
            elif c == "a":
                result += sides[0]
            else:
                result += sides[1]
        return result + "་"

    bo_num = "༠༡༢༣༤༥༦༧༨༩"
    sides = "ནབ"

    result = ""
    is_first_fn_passed = False
    for line in text.split("\n"):
        if not line:
            continue
        if line.startswith("[v"):
            continue
        if ":" in line:
            if is_first_fn_passed:
                result += f"{line}\n"
            else:
                result += f"\n{line}\n"
                is_first_fn_passed = True
        elif line.startswith("[") and line[1] != "^":
            en_pg_index = line.strip()[1:-1]
            bo_pg_index = index_to_bo(en_pg_index)
            result += f"({bo_pg_index})\n"
        else:
            result += f"{line}\n"

    return result


def create_foot_notes(text_id, opf_path, metadata, index_layer):
    serializer = SerializeFootNote(
        opf_path,
        text_id=text_id,
        index_layer=index_layer,
        layers=["correction", "peydurma-note", "pagination"],
    )
    if not serializer.text_spans:
        error_msg = f"[not-found] {text_id} not found in derge-tengyur\n"
        print(error_msg)
        error_logs_fn.open("a").write(error_msg)
        return ""
    serializer.apply_layers()
    annotated_text, text_id = serializer.get_result()

    bo_text = to_bo_pagination(annotated_text)
    return f'{bo_text[0]}{metadata[text_id]["loc"]} {bo_text[1:]}'


def get_text_metadata(path):
    import xml.dom.minidom as md

    from pyewts import pyewts

    converter = pyewts()

    def _text(tag_name, to_bo=False, is_loc=False):
        tag = item.getElementsByTagName(tag_name)
        if not tag:
            return "no-author"
        if not tag[0].firstChild:
            if tag_name == "author":
                return "no-author"
            else:
                return ""
        value = tag[0].firstChild.nodeValue.strip()
        if to_bo:
            return converter.toUnicode(value)
        if is_loc:
            name = converter.toUnicode(value.split(",")[0])
            vol = converter.toUnicode(value.split(",")[1].split(" ")[1])
            return f"{name}། {vol}"
        else:
            return value

    metadata = defaultdict(dict)
    dom = md.parseString(path.read_text())
    for item in dom.getElementsByTagName("item"):
        metadata[_text("ref")] = {
            "title": _text("tib", to_bo=True),
            "author": _text("author", to_bo=True),
            "loc": _text("loc", is_loc=True),
        }

    return metadata


def truncate_title(title):
    if len(title) > 70:
        return title[:35] + "_" + title[-35:]
    else:
        return title


if __name__ == "__main__":
    data_path = Path("../openpecha-user")
    opf_path = data_path / ".openpecha/data/P000002/P000002.opf"
    notes_path = data_path / "data" / "2-1-a_reinserted"
    text_metadata_path = data_path / "data" / "tanjurd.xml"
    foot_notes_path = data_path / "data" / "foot-notes"
    text_output_path = foot_notes_path / "txts"
    docx_output_path = foot_notes_path / "docxs"

    text_metadata = get_text_metadata(text_metadata_path)
    index_layer = yaml.safe_load((opf_path / "index.yml").open())

    for path in sorted(notes_path.iterdir()):
        text_id = path.name.split("_")[0]
        print(f"[INFO] Processing {text_id} ...")

        text_id = "D1943"
        if text_id not in text_metadata:
            error_msg = f"[not-found] {text_id} not found in derge-tengyur\n"
            print(error_msg)
            error_logs_fn.open("a").write(error_msg)
            continue

        # create output path for txt and docx file
        text_author_path = text_output_path / text_metadata[text_id]["author"]
        text_author_path.mkdir(exist_ok=True, parents=True)
        text_title = truncate_title(text_metadata[text_id]["title"])
        text_fn = text_author_path / f"{text_id}-{text_title}.txt"

        docx_author_path = docx_output_path / text_metadata[text_id]["author"]
        docx_author_path.mkdir(exist_ok=True, parents=True)
        docx_fn = docx_author_path / f"{text_id}-{text_title}.docx"
        if text_fn.is_file() and docx_fn.is_file():
            continue

        # create generate txt file
        foot_noted_text = create_foot_notes(
            text_id, opf_path, text_metadata, index_layer
        )
        if not foot_noted_text or "[^" not in foot_noted_text:
            continue
        text_fn.write_text(foot_noted_text)

        # convert txt file to docx with pandoc
        cmd = f"pandoc +RTS -K100000000 -RTS -s -o {docx_fn} {text_fn}"
        os.system(cmd)
        if docx_fn.is_file():
            print(f"[INFO] Generated {text_id} docx")
