from pathlib import Path
import re

import yaml
import diff_match_patch as dmp_module

from openpecha.github_utils import github_publish


def get_notes(fn):
    raw_text = fn.read_text()
    foot_note_idx = max(re.finditer(r'\[\^1K\]', raw_text), key=lambda x: x.start(0)).start(0)

    text_notes = []
    for line in raw_text[:foot_note_idx].split('\n'):
        if '[^' in line:
            note_start = line.index('[^')
            note_end = line.index(']')
            left_ct = line[:note_start]
            right_ct = line[note_end+1:]
            
            if 'a' in line:
                a_idx = line.index('a')
                if a_idx < note_start:
                    left_ct = line[a_idx+1:note_start]
                else:
                    right_ct = line[note_end+1: a_idx]
            
            text_notes.append((
                (left_ct, right_ct),
                line[note_start:note_end+1]
            ))

    foot_notes = {
        foot_note.split(':')[0]: foot_note.split(':')[1].strip() \
            for foot_note in raw_text[foot_note_idx:].split('\n')
    }

    return foot_notes, text_notes


def get_index(path):
    return yaml.safe_load((path/'index.yml').open())


def get_layer_ann(path, vol, layer_name):
    return yaml.safe_load((path/'layers'/vol/f'{layer_name}.yml').open())


def save_layer_ann(layer_ann, path, vol, layer_name):
    return yaml.safe_dump(
        layer_ann,
        (path/'layers'/vol/f'{layer_name}.yml').open('w'),
        default_flow_style=False,
        sort_keys=False, 
        allow_unicode=True
    )


def get_work_text(path, vol):
    span = vol['span']
    return (path/f"{vol['vol']}.txt").read_text()[span['start']: span['end']+1]


def update_layer(note_idx, vol, layer_ann, note):
    vol_note_idx = note_idx + vol['span']['start']
    for ann in layer_ann['annotations']:
        if abs(ann['span']['start']-vol_note_idx) <= 2:
            ann['note'] = note
            break


def reinsert(pecha_path, notes_path, layer_name):
    pecha_opf_path = pecha_path/f'{pecha_path.name}.opf'
    pecha_index = get_index(pecha_opf_path)

    layer_ann = None
    prev_vol = None
    for text_ann in pecha_index['annotations']:
        notes_fn = notes_path/f'{text_ann["work"]}_a_reinserted.txt'
        if not notes_fn.is_file(): continue
        print(notes_fn)
        foot_notes, text_notes = get_notes(notes_fn)

        # cross-vol text have mutlitple layer files in terms of volume
        for vol in text_ann['span']:
            work_text = get_work_text(pecha_opf_path, vol)
            if prev_vol != vol['vol']:
                # first save the layer of previous volume.
                if layer_ann:
                    save_layer_ann(layer_ann, pecha_opf_path, prev_vol[5:], layer_name)
                
                # then load the layer of next volume
                layer_ann = get_layer_ann(pecha_opf_path, vol['vol'][5:], layer_name)

            # insert each foot_note of current text into layer with note_idx.
            for text_note in text_notes:
                print(text_note)
                context = text_note[0]
                is_right_ct_longer = len(context[1]) > len(context[0])
                note_idx = None
                if is_right_ct_longer:
                    note_idx = work_text.find(context[1])
                else:
                    right_ct_idx = work_text.find(context[0])
                    note_idx = right_ct_idx + len(context[0])
                
                if note_idx:
                    update_layer(note_idx, vol, layer_ann, foot_notes[text_note[1]])

            prev_vol = vol['vol']


if __name__ == "__main__":
    DATA_PATH = Path('../openpecha-user')
    OPF_PECHA_PATH = DATA_PATH/'.openpecha/data/P000002'
    NOTES_PATH = DATA_PATH/'data'/'2-1-a_reinserted'
    
    reinsert(OPF_PECHA_PATH, NOTES_PATH, 'peydurma')