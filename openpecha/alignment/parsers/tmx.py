import re
from pathlib import Path

from bs4 import BeautifulSoup


def parse_segment(multilingual_segment, src_lang, tar_lang):
    src_seg = ""
    tar_seg = ""
    segments = multilingual_segment.find_all("tuv")
    for segment in segments:
        seg_text = segment.find("seg").text if segment.find("seg").text else "-----"
        seg_text = re.sub(r"\n|\t", " ", seg_text)
        seg_text = re.sub(r"\s{2,}", " ", seg_text)
        seg_text = seg_text.strip() + "\n"
        if segment.get("xml:lang", "") == src_lang:
            src_seg = seg_text
        elif segment.get("xml:lang", "") == tar_lang:
            tar_seg = seg_text
    return [src_seg, tar_seg]


def parse_tmx_text(tmx_content, src_lang="bo", tar_lang="en"):
    tmx_text = {src_lang: "", tar_lang: ""}
    soup = BeautifulSoup(tmx_content, "xml")
    multilingual_segments = soup.find_all("tu")
    for multilingual_segment in multilingual_segments:
        src_seg, tar_seg = parse_segment(multilingual_segment, src_lang, tar_lang)
        tmx_text[src_lang] += src_seg
        tmx_text[tar_lang] += tar_seg
    return tmx_text


def normalise_dict_keys(dict_obj):
    """replaces `:` to `-` in dict"""

    result = {}
    for key, value in dict_obj.items():
        key = key.replace(":", "-")
        result[key] = value
    return result


def parse_metadata(tmx):
    soup = BeautifulSoup(tmx, "xml")
    source_metadata = soup.header.attrs
    source_metadata = normalise_dict_keys(source_metadata)
    return source_metadata


def parse_tmx(tmx_path):
    tmx = tmx_path.read_text(encoding="utf-8-sig")
    source_metadata = parse_metadata(tmx)
    src_lang = source_metadata.get("srclang", "")
    tar_lang = source_metadata.get("adminlang", "")
    if re.search(r"en", tar_lang):
        tar_lang = "en"
    tmx_text = parse_tmx_text(tmx, src_lang, tar_lang)
    src_text = tmx_text[src_lang]
    tar_text = tmx_text[tar_lang]
    tar_text = re.sub(r"\d+", "", tar_text)
    tar_text = tar_text.replace("[]", "")
    tar_text = tar_text.replace("()", "")
    tar_text = tar_text.replace(r"{}", "")
    return src_text, tar_text, source_metadata
