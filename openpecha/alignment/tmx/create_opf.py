"""This module is to create pecha opf and alignment opa
Avialable functions:
    create_alignment_from_source_text: It will create pecha opf and alignment opa from a source text.
    create_alignment_from_tmx: It will create source and target opf and alignment opa from tmx path.
"""

import os
from pathlib import Path
from uuid import uuid4

from openpecha import config, github_utils
from openpecha.core.annotation import AnnBase, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import dump_yaml, load_yaml

from ..parsers.tmx import parse_tmx
from ..segmenters.sentence import get_sentence_segments
from . import TMXAlignment


def get_segment_annotation(segment, char_walker):
    seg_len = len(segment) - 1
    segment_annotation = {
        uuid4().hex: AnnBase(span=Span(start=char_walker, end=char_walker + seg_len))
    }
    return segment_annotation, (char_walker + seg_len)


def get_segment_layer(text):
    segment_annotations = {}
    char_walker = 0
    segments = text.splitlines()
    for segment in segments:
        if segment:
            segment_annotation, end = get_segment_annotation(segment, char_walker)
            segment_annotations.update(segment_annotation)
        char_walker = end + 2

    segment_layer = Layer(
        annotation_type=LayerEnum.segment, annotations=segment_annotations
    )
    return segment_layer


def get_base_text(text):
    final_base = ""
    segments = text.splitlines()
    for segment in segments:
        final_base += segment + "\n"
    return final_base


def create_opf_repo(segmented_text, opf_path, title, lang, origin_type):
    pecha_id = opf_path.stem
    opf = OpenPechaFS(path=opf_path)
    layers = {"0001": {LayerEnum.segment: get_segment_layer(segmented_text)}}
    base_text = get_base_text(segmented_text)
    bases = {"0001": base_text}
    metadata = {
        "id": pecha_id,
        "initial_creation_type": "TMX",
        "origin_type": origin_type,
        "source_metadata": {
            "id": "",
            "title": title,
            "language": lang,
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


def create_readme(pecha_path):
    pecha_id = pecha_path.stem
    meta_yml = load_yaml((pecha_path / f"{pecha_id}.opf/meta.yml"))
    pecha = f"|Pecha id | {pecha_id}"
    Table = "| --- | --- "
    Title = f"|Title | {meta_yml.get('source_metadata', {}).get('title', None)} "
    type = f"|Type | {meta_yml.get('origin_type', None)}"
    lang = f"|Language | {meta_yml.get('source_metadata',{}).get('language', None)}"
    Creator = f"|Initial creation | { meta_yml.get('initial_creation_type', None)}"
    readme = f"{pecha}\n{Table}\n{Title}\n{lang}\n{type}\n{Creator}"
    return readme


def create_opf(text, title=None, lang=None, origin_type="translation", new=False):
    if text:
        if new:
            text = get_sentence_segments(text)
        pecha_id = uuid4().hex
        opf_path = config.PECHAS_PATH / pecha_id / f"{pecha_id}.opf"
        create_opf_repo(text, opf_path, title, lang, origin_type)
        readme = create_readme(opf_path.parent)
        (opf_path.parent / "readme.md").write_text(readme, encoding="utf-8")
    return opf_path.parent


def publish_pecha(pecha_path):
    github_utils.github_publish(
        pecha_path,
        message="initial commit",
        not_includes=[],
        layers=[],
        org="Openpecha",
        token=os.environ.get("GITHUB_TOKEN"),
    )


def create_opf_from_tmx(tmx_path):
    title = tmx_path.stem

    src_text, tar_text, source_metadata = parse_tmx(tmx_path)
    if source_metadata["creationtool"] == "84000-translation-memory":
        origin_type = "translation"
    elif source_metadata["creationtool"] == "InterText":
        origin_type = "translation"
    else:
        origin_type = None

    src_lang = source_metadata.get("srclang", "")
    tar_lang = source_metadata.get("adminlang", "")

    source_pecha_path = create_opf(src_text, title, src_lang, origin_type)
    target_pecha_path = create_opf(tar_text, title, tar_lang, origin_type)

    return source_pecha_path, target_pecha_path, source_metadata


def create_alignment_from_source_text(text_path, title, publish=True):
    text = Path(text_path).read_text(encoding="utf-8")
    opf_path = create_opf(text, title=None, lang=None, new=True)
    obj = TMXAlignment()
    alignment_path = obj.create_alignment_repo(
        source_pecha_path=opf_path,
        target_pecha_path=None,
        title=title,
        source_metadata=None,
    )
    if publish:
        publish_pecha(opf_path)
        publish_pecha(alignment_path)
    return alignment_path


def create_alignment(source_pecha_path, target_pecha_path, title, source_metadata):
    obj = TMXAlignment()
    alignment_path = obj.create_alignment_repo(
        source_pecha_path, target_pecha_path, title, source_metadata
    )
    return alignment_path


def create_alignment_from_tmx(tmx_path, publish=True):
    title = tmx_path.stem
    source_pecha_path, target_pecha_path, source_metadata = create_opf_from_tmx(
        tmx_path
    )
    alignment_path = create_alignment(
        source_pecha_path, target_pecha_path, title, source_metadata
    )

    if publish:
        publish_pecha(source_pecha_path)
        publish_pecha(target_pecha_path)
        publish_pecha(alignment_path)

    return alignment_path
