import re
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

import diff_match_patch as dmp_module
import yaml

from openpecha.blupdate import Blupdate
from openpecha.formatters import BaseFormatter
from openpecha.formatters.format import Layer, Peydurma

error_log_fn = Path("./error_logs") / Path(__file__).stem
if error_log_fn.is_file():
    error_log_fn.unlink()


def get_notes(fn):
    raw_text = fn.read_text()
    if "[^" not in raw_text:
        return None, None
    pattern = r""
    if "[^1K]" in raw_text:
        pattern = r"\[\^1K\]"
    else:
        pattern = r"\[\^2K\]"
    foot_note_idx = max(re.finditer(pattern, raw_text), key=lambda x: x.start(0)).start(
        0
    )

    # preprocess text
    text = raw_text[: foot_note_idx - 1].replace("\ufeff", "")
    text = text[1:] if text[0] == "a" else text
    text = text.replace("\n", " ")
    text = text.replace("a", "\n")

    is_note = False
    base_text_len = 0
    text_notes = []
    base_text = ""
    for i, c in enumerate(text):
        if c == "[" and text[i + 1] == "^":
            is_note = True
        elif is_note and c == "]":
            is_note = False
            text_notes.append(base_text_len - 1)
        elif not is_note:
            base_text_len += 1
            base_text += c

    foot_notes = [
        foot_note.split(":")[1].strip()
        for foot_note in raw_text[foot_note_idx:].split("\n")
        if foot_note
    ]

    return zip(text_notes, foot_notes), base_text.strip()


def get_index(path):
    return yaml.safe_load((path / "index.yml").open())


def get_layer_ann(path, vol, layer_name):
    return yaml.safe_load((path / "layers" / vol / f"{layer_name}.yml").open())


def save_layer_ann(layer_ann, path, vol, layer_name):
    return yaml.safe_dump(
        layer_ann,
        (path / "layers" / vol / f"{layer_name}.yml").open("w"),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


def create_layer(layer_name):
    layer = deepcopy(Layer)
    layer["id"] = BaseFormatter().get_unique_id()
    layer["annotation_type"] = layer_name
    layer["revision"] = f"{1:05}"
    return layer


def get_work_text(path, vol):
    span = vol["span"]
    return (path / f"{vol['vol']}.txt").read_text()[span["start"] : span["end"]]


def update_layer(note, bl, note_idx, vol, layer_ann):
    dst_note_idx = bl.get_updated_coord(note[0])
    if dst_note_idx == -1:
        return
    vol_note_idx = dst_note_idx + vol["span"]["start"]

    if layer_ann["annotations"] and len(layer_ann["annotations"]) > note_idx + 1:
        ann = layer_ann["annotations"][0]
        ann["note"] = note[1]
        ann["span"] = vol_note_idx
        ann["span"] = vol_note_idx
    else:
        peydurma = deepcopy(Peydurma)
        peydurma["id"] = BaseFormatter().get_unique_id()
        peydurma["note"] = note[1]
        peydurma["span"]["start"] = vol_note_idx
        peydurma["span"]["end"] = vol_note_idx
        layer_ann["annotations"].append(peydurma)


def reinsert(pecha_path, notes_path, layer_name):
    pecha_opf_path = pecha_path / f"{pecha_path.name}.opf"
    pecha_index = get_index(pecha_opf_path)

    layer_ann = None
    prev_vol = None
    note_idx = 0
    for text_ann in pecha_index["annotations"]:
        notes_fn = notes_path / f'{text_ann["work"]}_a_reinserted.txt'
        if not notes_fn.is_file():
            continue
        # if not text_ann['work'] == 'D1115': continue
        print(f'[INFO] Processing {text_ann["work"]} ...')
        notes, base_text = get_notes(notes_fn)
        if not notes:
            continue

        # cross-vol text have mutlitple layer files in terms of volume
        for vol in text_ann["span"]:
            work_text = get_work_text(pecha_opf_path, vol)
            if prev_vol != vol["vol"]:
                # first save the layer of previous volume.
                if layer_ann:
                    save_layer_ann(layer_ann, pecha_opf_path, prev_vol[5:], layer_name)

                # then load the layer of next volume
                if layer_name in ["peydurma"]:
                    layer_ann = get_layer_ann(
                        pecha_opf_path, vol["vol"][5:], layer_name
                    )
                else:
                    layer_ann = create_layer(layer_name)

                note_idx = 0

            # insert each foot_note of current text into layer with note_idx.
            bl = Blupdate(base_text, work_text)
            if len(bl.cctv) <= 1:
                error_msg = f'[diff-text] {text_ann["work"]} (derge-tengyur)\n'
                print(error_msg)
                error_log_fn.open("a").write(error_msg)
                break
            for note in notes:
                update_layer(note, bl, note_idx, vol, layer_ann)
                note_idx += 1

            prev_vol = vol["vol"]


if __name__ == "__main__":
    DATA_PATH = Path("../openpecha-user")
    OPF_PECHA_PATH = DATA_PATH / ".openpecha/data/P000002"
    NOTES_PATH = DATA_PATH / "data" / "2-1-a_reinserted"

    reinsert(OPF_PECHA_PATH, NOTES_PATH, "peydurma-note")
