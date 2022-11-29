"""This module is to create pecha opf and alignment opa
Avialable functions:
    create_alignment_from_source_text: It will create pecha opf and alignment opa from a source text.
    create_alignment_from_tmx: It will create source and target opf and alignment opa from tmx path.
"""

import os
from pathlib import Path
from uuid import uuid4
import datetime
from datetime import timezone
from enum import Enum

from openpecha import config, github_utils
from openpecha.core.annotation import AnnBase, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml, dump_yaml
from openpecha.core.ids import get_base_id, get_initial_pecha_id
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType

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


def get_metadata(pecha_id: str = None, title: str = None, language: str = None) -> InitialPechaMetadata:
        source_metadata = {
            "id": "",
            "title": title,
            "author": "",
        }
        copyright = {}
        license = None
        parser_link = None

        metadata = InitialPechaMetadata(
            id=pecha_id,
            source='',
            initial_creation_type=InitialCreationType.tmx,
            imported=datetime.datetime.now(timezone.utc),
            last_modified=datetime.datetime.now(timezone.utc),
            parser=parser_link,
            copyright=copyright,
            license=license,
            source_metadata=source_metadata,
            default_language=language
        )
        return metadata


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


def create_opf(segmented_text, title=None, lang=None, output_path=None, new=False):
    if segmented_text:
        if new:
            text = get_sentence_segments(segmented_text)
        else:
            text = segmented_text
    pecha_id = get_initial_pecha_id()
    # opf_path = config.PECHAS_PATH / pecha_id / f"{pecha_id}.opf"
    opf_path = Path(f"{output_path}/{pecha_id}/{pecha_id}.opf")
    opf_path.mkdir(exist_ok=True, parents=True)
    pecha = OpenPechaFS(path=opf_path)
    base_id = get_base_id()
    layers = {f"{base_id}": {LayerEnum.segment: get_segment_layer(text)}}
    base_text = get_base_text(text)
    bases = {f"{base_id}": base_text}
    metadata = get_metadata(pecha_id, title, lang)
    pecha.layers = layers
    pecha.bases = bases
    pecha.metadata = metadata 
    pecha.metadata.bases = {
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
    # pecha.save_meta()
    
    metadata = pecha.metadata
    dump_yaml(metadata, pecha.meta_fn)
    readme = create_readme(pecha.pecha_path.parent)
    (pecha.pecha_path.parent / "readme.md").write_text(readme, encoding="utf-8")
    return pecha


def publish_pecha(pecha_path):
    github_utils.github_publish(
        pecha_path,
        message="initial commit",
        not_includes=[],
        layers=[],
        org=os.environ.get("OPENPECHA_DATA_GITHUB_ORG"),
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


def create_alignment_from_source_text(text_path, title, lang, output_path, publish=True):
    text = Path(text_path).read_text(encoding="utf-8")
    pecha = create_opf(text, title, lang, output_path, new=True)
    obj = TMXAlignment()
    alignment_path = obj.create_alignment_repo(
        source_pecha_path=pecha.pecha_path,
        target_pecha_path=None,
        title=title,
        source_metadata=None,
    )
    if publish:
        pecha.publish()
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
