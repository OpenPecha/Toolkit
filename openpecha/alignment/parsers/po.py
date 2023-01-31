import os
import re
from pathlib import Path
from uuid import uuid4

import polib
from git import Repo

from openpecha import config
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaGitRepo
from openpecha.core.ids import get_base_id, get_initial_pecha_id
from openpecha.github_utils import commit
from openpecha.utils import dump_yaml

from ...alignment.tmx import TMXAlignment
from ...alignment.tmx.create_opf import (
    create_readme,
    get_segment_annotation,
    get_metadata
    )


def setup_auth(repo, org, token):
    remote_url = repo.remote().url
    old_url = remote_url.split("//")
    authed_remote_url = f"{old_url[0]}//{org}:{token}@{old_url[1]}"
    repo.remote().set_url(authed_remote_url)


def get_segment_layer_base_and_mapping(po_dict):
    segment_annotations = {}
    char_walker = 0
    base_text = ""
    annotation_map = {}
    curr_dict = {}
    for uid, text_info in po_dict.items():
        text = text_info["text"]
        segment_annotation, end = get_segment_annotation(text, char_walker)
        segment_annotations.update(segment_annotation)
        char_walker = end + 2
        annotation_id = list(segment_annotation.keys())[0]
        base_text += text + "\n"
        curr_dict[uid] = {"annotation_id": annotation_id}
        annotation_map.update(curr_dict)
        curr_dict = {}

    segment_layer = Layer(
        annotation_type=LayerEnum.segment, annotations=segment_annotations
    )
    return segment_layer, base_text, annotation_map


def create_opf_for_translated(po_dict, title=None, lang=None):
    source_metadata = {}
    segment_layer, base_text, annotation_map = get_segment_layer_base_and_mapping(
        po_dict
    )
    pecha_id = get_initial_pecha_id()
    opf_path = config.PECHAS_PATH / pecha_id / f"{pecha_id}.opf"
    opf_path.mkdir(exist_ok=True, parents=True)
    pecha = OpenPechaGitRepo(path=opf_path)
    base_id = get_base_id()
    layers = {f"{base_id}": {LayerEnum.segment: segment_layer}}
    base_text = base_text
    bases = {f"{base_id}": base_text}
    source_metadata.update({'title':title})
    metadata = get_metadata(pecha_id, lang, source_metadata)
    pecha.layers = layers
    pecha.bases = bases
    pecha._meta = metadata
    
    pecha._meta.bases = {
        base_id:
            {   
                "source_metadata": None,
                "order": 1,
                "base_file": f"{base_id}.txt",
                "statistics": None
                }
            }
    pecha.save_base()
    pecha.save_layers()
    pecha.save_meta()
    readme = create_readme(pecha.pecha_path)
    (pecha.pecha_path / "readme.md").write_text(readme, encoding="utf-8")
    return pecha, annotation_map


def create_opf_and_annotation_map(po_zip, title=None, lang=None):
    if po_zip:
        pecha, annotation_map = create_opf_for_translated(
            po_zip, title, lang
        )
    return pecha, annotation_map


def get_id_and_string(po_file):
    po_dict = {}
    curr_po = {}
    lang = po_file.metadata["Language"]
    for entry in po_file:
        if lang == "bo":
            id = entry.msgid
            string = entry.tcomment
        elif lang == "en":
            id = entry.msgid
            string = entry.msgstr
        text = re.sub(r"\n", " ", string)
        curr_po[id] = {"text": text}
        po_dict.update(curr_po)
        curr_po = {}
    return po_dict, lang


def transifex_output_to_opf(po_path):
    po_file = polib.pofile(po_path)
    po_zip, lang = get_id_and_string(po_file)
    title = "this is the title"
    target_pecha, annotation_map = create_opf_and_annotation_map(
        po_zip, title, lang
    )
    return target_pecha, annotation_map


def update_alignment_from_po(po_path, alignment_path, publish=True):
    target_pecha, annotation_map = transifex_output_to_opf(po_path)
    obj = TMXAlignment()
    obj.update_alignment_repo(alignment_path, target_pecha.pecha_path, annotation_map)

    if publish:
        repo = Repo(alignment_path)
        token = os.environ.get("GITHUB_TOKEN")
        org = os.environ["OPENPECHA_DATA_GITHUB_ORG"]
        setup_auth(repo, org, token)
        message = "updated alginment.yml"
        commit(repo, message, not_includes=[], branch="master")
        target_pecha.publish()
    return target_pecha.pecha_path
