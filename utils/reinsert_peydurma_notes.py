from pathlib import Path
import re

import yaml


def preprocess_notes(fn):
    raw_text = fn.read_text()
    foot_note_index = max(re.finditer(r'\[\^1K\]', raw_text), key=lambda x: x.start(0)).start(0)
    text = raw_text[:foot_note_index]
    foot_notes = raw_text[foot_note_index:].split('\n')
    return text, foot_notes


def reinsert(pecha_path, note_fn):
       text, foot_notes = preprocess_notes(note_fn) 
       print(text, foot_notes)


if __name__ == "__main__":
    DATA_PATH = Path('../openpecha-user')
    OPF_PECHA_PATH = DATA_PATH/'.openpecha/data/P000002'
    NOTES_PATH = DATA_PATH/'data'/'2-1-a_reinserted'
    
    # test_note_fn = NOTES_PATH/'D1115_a_reinserted.txt'
    # reinsert(OPF_PECHA_PATH, test_note_fn)




    for notes_fn in NOTES_PATH.iterdir():
        reinsert(OPF_PECHA_PATH, notes_fn)