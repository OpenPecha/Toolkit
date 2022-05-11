import re
from pathlib import Path
from uuid import uuid4

import polib
from create_opf import create_readme, get_segment_annotation

from openpecha import config
from openpecha.core.annotation import AnnBase, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import dump_yaml, load_yaml

from . import TMXAlignment


def read_po(path):
    return polib.pofile(path)


def get_id_and_string(po_file):
    po_dict = {}
    curr_po = {}
    for entry in po_file:
        id = entry.msgid
        string = entry.msgstr
        text = re.sub(r"\n", " ", string)
        curr_po[id] = {text}
        po_dict.update(curr_po)
        curr_po = {}
    return po_dict


def get_segment_layer_base_and_mapping(po_dict):
    segment_annotations = {}
    char_walker = 0
    base_text = ""
    annotation_map = {}
    curr_dict = {}
    for uid, text in po_dict.items():
        segment_annotation, end = get_segment_annotation(text, char_walker)
        segment_annotations.update(segment_annotation)
        char_walker = end + 2
        annotation_id = list(segment_annotation.keys())[0]
        base_text += list(text)[0] + "\n"
        curr_dict[uid] = {annotation_id}
        annotation_map.update(curr_dict)
        curr_dict = {}

    segment_layer = Layer(
        annotation_type=LayerEnum.segment, annotations=segment_annotations
    )
    return segment_layer, base_text, annotation_map


def create_opf_for_translated(
    po_dict, pecha_id, opf_path, title=None, origin_type="translation", lan=None
):
    opf = OpenPechaFS(path=opf_path)
    segment_layer, base_text, annotation_map = get_segment_layer_base_and_mapping(
        po_dict
    )
    layers = {"0001": {LayerEnum.segment: segment_layer}}
    bases = {"0001": base_text}
    metadata = {
        "id": pecha_id,
        "initial_creation_type": "TMX",
        "origin_type": origin_type,
        "source_metadata": {
            "id": "",
            "title": title,
            "langauge": lan,
            "author": "",
            "volume": {},
        },
    }
    opf.layers = layers
    opf.base = bases
    opf.save_base()
    opf.save_layers()
    meta_fn = Path(f"{opf_path}/meta.yml")
    dump_yaml(metadata, meta_fn)
    return annotation_map


def get_opf_path_and_annotation_map(po_zip, title, lan):
    if po_zip:
        pecha_id = uuid4().hex
        opf_path = config.PECHAS_PATH / pecha_id / f"{pecha_id}.opf/"
        annotation_map = create_opf_for_translated(
            po_zip, pecha_id, opf_path, title, lan=lan
        )
        readme = create_readme(pecha_id)
        Path(config.PECHAS_PATH / pecha_id / "readme.md").write_text(
            readme, encoding="utf-8"
        )
    return opf_path, annotation_map


def update_alignment_from_po(po_path):
    po_file = read_po(po_path)
    po_zip = get_id_and_string(po_file)
    lan = "bo"
    title = ""
    pecha_id, annotation_map = get_opf_path_and_annotation_map(po_zip, title, lan)
    alignment_id = ""
    alignment_repo = config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa"
    obj = TMXAlignment
    obj.update_alignment_repo(
        alignment_repo=alignment_repo,
        target_pecha_id=pecha_id,
        annotation_map=annotation_map,
        lan=lan,
    )
