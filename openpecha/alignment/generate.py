from pathlib import Path

from openpecha.utils import load_yaml


def get_src_bases(src_paths):
    """Return base text as value and key as src name

    Args:
        src_paths (dict): src name as key and src path as value

    Returns:
        dict: src name as key and src base text as value
    """
    src_bases = {}
    for src_name, src_path in src_paths.items():
        try:
            src_bases[src_name] = (
                Path(src_path) / f"{src_name}.opf/bases/v001.txt"
            ).read_text(encoding="utf-8")
        except Exception:
            src_bases[src_name] = ""
    return src_bases


def get_segment_layer(pecha_id, pecha_path):
    """Return src pecha's segment annotations detail from segment layer

    Args:
        pecha_id (str): pecha id
        pecha_path (str): pecha path

    Returns:
        dict: segment annotations detail
    """
    try:
        segment_layer = load_yaml(
            (Path(pecha_path) / f"{pecha_id}.opf/layers/v001/Segment.yml")
        )
        segment_annotations = segment_layer["annotations"]
        return segment_annotations
    except Exception:
        return {}


def get_segment_annotations(segment_src_paths):
    """return dictionary with key as src name and src segment annotations as value

    Args:
        segment_src_paths (dict): key as src name and value as src paths

    Returns:
        dict: key as src name and src segment annotations as value
    """
    segment_annotations = {}
    for segment_src_pecha_id, segment_src_pecha_path in segment_src_paths.items():
        segment_annotations[segment_src_pecha_id] = get_segment_layer(
            segment_src_pecha_id, segment_src_pecha_path
        )
    return segment_annotations


def get_segment(segment_ann, src_bases, segment_src):
    """Extract segment text and return

    Args:
        segment_ann (dict): segment annotation detail
        src_bases (dict): key as src name and value as src base text
        segment_src (str): segment src instance or work name

    Returns:
        str: segment text from src base
    """
    segment_text = ""
    if segment_ann:
        src_base = src_bases[segment_src]
        segment_start = segment_ann["span"]["start"]
        segment_end = segment_ann["span"]["end"]
        segment_text = src_base[segment_start : segment_end + 1]
    return segment_text


def get_segment_text(segment_annotations, src_bases, segment_pair):
    """extract all the segment text from respective src

    Args:
        segment_annotations (dict): key as src name and value as segment annotation
        src_bases (dict): key as src name and value as src base
        segment_pair (dict): key as segment id in alignment file and value as src with its segment annotation id

    Returns:
        str: segment text
    """
    segment_text = ""
    for segment_src, segment_id in segment_pair.items():
        segment_ann = segment_annotations[segment_src].get(segment_id, {})
        segment_text += get_segment(segment_ann, src_bases, segment_src) + "\n"
    return segment_text


def get_segment_pairs(segment_src_paths, segment_pairs):
    """Using segment pairs attribute of alignment object, generate parallel text in string format

    Args:
        segment_src_paths (dict): key as segment src instance or work id and value as opf path of respective instance or work
        segment_pairs (dict): key as segment id and value as src with its segment annotation id in their opf

    Returns:
        str: each segment is seperated by two line break and within each segment multiple src text are seperated by one line break
    """
    alignment_text = ""
    segment_annotations = get_segment_annotations(segment_src_paths)
    src_bases = get_src_bases(segment_src_paths)
    for segment_id, segment_pair in segment_pairs.items():
        alignment_text += f"{segment_id}\n{get_segment_text(segment_annotations, src_bases, segment_pair)}\n"
    return alignment_text
