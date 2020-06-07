import re
from collections import defaultdict

ann_patterns = {
    "peydurma_page": {
        "start": "<p",
        "end": ">",
        "has_text": False,
        "has_payload": True,
        "payload_pattern": "(.*?)",
    },
    "img_url": {
        "start": "\[https",
        "end": "\]",
        "has_text": False,
        "has_payload": True,
        "payload_pattern": "(.*?)",
    },
    "correction": {
        "start": "\(",
        "end": "\)",
        "has_text": True,
        "has_payload": True,
        "payload_pattern": ".*?,(.*?)",
        "payload_sep_len": 1,
    },
}


def sort_by_pos(matches):
    """Sort `matches` by start char position"""
    return sorted(matches, key=lambda x: x[1].span(0)[0])


def get_base_idx(ann, offset, is_end=False, payload_len=0):
    start, end = ann.span(0)
    marker_len = end - start
    if is_end:
        offset += marker_len + payload_len
        base_idx = end - offset
        return base_idx, offset

    base_idx = start - offset
    offset += marker_len
    return base_idx, offset


def get_markers(name, pattern, text):
    return [(name, m) for m in re.finditer(pattern, text)]


def get_payload(name, start_match, end_match, text):
    start = start_match.span(0)[0]
    end = end_match.span(0)[1]
    search_text = text[start:end]
    ann = ann_patterns[name]
    payload_pattern = f'{ann["start"]}{ann["payload_pattern"]}{ann["end"]}'
    payload = re.findall(payload_pattern, search_text)[0]
    return payload


def parse_annotations(text, ann_patterns):
    # Find start and end of annotation separately
    # TODO: apply multiprocessing on patterns
    ann_start_markers, ann_ends_markers = [], []
    for name in ann_patterns:
        ann_start_markers.extend(get_markers(name, ann_patterns[name]["start"], text))
        ann_ends_markers.extend(get_markers(name, ann_patterns[name]["end"], text))

    # Sort all_starts and all_ends sperately
    ann_start_markers = sort_by_pos(ann_start_markers)
    ann_ends_markers = sort_by_pos(ann_ends_markers)

    # Find ann_start and ann_end pair
    anns = defaultdict(list)
    s_idx, e_idx = 0, 0
    offset = 0
    while s_idx < len(ann_start_markers) or e_idx < len(ann_ends_markers):
        #         import pdb; pdb.set_trace()
        payload = 0
        ann_name, ann_start_match = ann_start_markers[s_idx]
        _, ann_end_match = ann_ends_markers[e_idx]
        base_start, offset = get_base_idx(ann_start_match, offset)

        # ann which includes text
        if ann_patterns[ann_name]["has_text"]:
            # ann with payload
            if ann_patterns[ann_name]["has_payload"]:
                payload = get_payload(ann_name, ann_start_match, ann_end_match, text)
                payload_len = len(payload) + ann_patterns[ann_name]["payload_sep_len"]
            base_end, offset = get_base_idx(
                ann_end_match, offset, is_end=True, payload_len=payload_len
            )

            anns[ann_name].append((base_start, base_end, payload))
        # ann which doesn't includes text
        else:
            # ann with payload
            if ann_patterns[ann_name]["has_payload"]:
                payload = get_payload(ann_name, ann_start_match, ann_end_match, text)
            _, offset = get_base_idx(
                ann_end_match, offset, is_end=True, payload_len=len(payload)
            )
            anns[ann_name].append((base_start, None, payload))

        s_idx += 1
        e_idx += 1

    return anns
