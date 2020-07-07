"""
Formatter for HFML annotations in the text

This module implements all classes necessary to format HFML annotation to OpenPecha format.
HFML (Human Friendly Markup Language) contains tagset used for structuring and annotating the text.
"""
import re
from collections import defaultdict
from pathlib import Path

from openpecha.formatters.formatter import BaseFormatter
from openpecha.formatters.layers import *


class Global2LocalId:
    """Map global id of annotation in a layer to local id of a layer."""

    def __init__(self, local_id_dict):
        self.start_local_id = 200_000
        self.global2local_id = self._initialize(local_id_dict)
        self.local2global_id = {
            l_id: g_id for l_id, g_id in self.global2local_id.items()
        }
        self.last_local_id = self.find_last()

    def _initialize(self, local_id_dict):
        g2lid = {}
        for global_id, local_id in local_id_dict.items():
            g2lid[global_id] = {"local_id": local_id, "is_found": False}
        return g2lid

    def find_last(self):
        """Return last local id in a layer."""
        if self.global2local_id:
            return list(self.global2local_id.values()).pop()["local_id"]
        return chr(self.start_local_id - 1)

    def add(self, global_id):
        """Map given `global_id` to the last local id."""
        next_local_id = chr(ord(self.last_local_id) + 1)
        self.global2local_id[global_id] = next_local_id
        self.last_local_id = next_local_id

    def get_local_id(self, global_id):
        """Return `local_id` associated to given `global_id`."""
        return self.global2local_id.get(global_id, None)

    def get_global_id(self, local_id):
        """Return `global_id` associated to given `local_id`."""
        return self.local2global_id.get(local_id, None)

    def serialize(self):
        """Return just the global and local id paris."""
        result = {}
        for global_id, id_obj in self.global2local_id.items():
            if isinstance(id_obj, str):
                result[global_id] = id_obj
            elif id_obj["is_found"]:
                result[global_id] = id_obj["is_found"]
        return result


class LocalIdManager:
    """Maintains local_id to uuid map for echa layer."""

    def __init__(self, layers):
        self.map_name = "uuid2local-id"
        self.maps = self._get_local_id_maps(layers)

    def _get_local_id_maps(self, layers):
        maps = {}
        for layer in layers:
            maps[layer] = Global2LocalId(layers[layer].get(self.map_name, {}))
        return maps

    def add(self, layer_name, global_id):
        """Add `global_id` to layer's global2local id map."""
        self.maps[layer_name].add(global_id)

    def serialize(self, layer_name):
        """Convert map of given `layer_name` in global and local id pairs."""
        return self.maps[layer_name].serialize()


ANN_PATTERN = {
    AnnType.peydurma: {
        "start": "<p",
        "end": ">",
        "has_text": False,
        "has_payload": True,
        "payload_pattern": "(.*?)",
    },
    AnnType.correction: {
        "start": "\(",
        "end": "\)",
        "has_text": True,
        "has_payload": True,
        "payload_pattern": ".*?,(.*?)",
        "payload_sep_len": 1,
    },
}


class HFMLFormatter(BaseFormatter):
    """
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    """

    def __init__(self, output_path="./output", is_book=False, config=None):
        super().__init__(output_path=output_path)
        self.config = config
        self.is_book = is_book
        self.base_text = ""
        self.layers = defaultdict(defaultdict(list))

    def text_preprocess(self, text):
        if text[0] == "\ufeff":
            text = text[1:]

        if not self.is_book:
            return text

        p = r"\[p\]"
        lines = text.splitlines()
        result_text = ""
        para = False
        for line in lines:
            if re.search(p, line):
                if para:
                    para = False
                    result_text += "\n"
                else:
                    para = True
            elif re.search(p, line) == None:
                if para:
                    result_text += line
                else:
                    result_text += line + "\n"
        return result_text

    def get_input(self, input_path):
        fns = list(input_path.iterdir())
        fns_len = len(fns)
        for fn in sorted(fns):
            yield self.text_preprocess(fn.read_text()), fn.name, fns_len

    def get_old_layers(self, new_layers):
        layers = {}
        for layer in new_layers:
            layer_fn = self.dirs["layers_path"] / f"{layer}.yml"
            if layer_fn.is_file():
                layers[layer] = self.load(layer_fn)
        return layers

    def _inc_layer_revision(self, layer):
        inc_rev_int = int(layer["revision"]) + 1
        layer["revision"] = f"{inc_rev_int:05}"

    def add_new_ann(self, layer, ann):
        uuid = self.get_unique_id()
        layer["annotations"][uuid] = ann
        self.local_id_manager.add(layer["annotation_type"], uuid)

    def create_new_layer(self, layer_name, anns):
        new_layer = Layer(self.get_unique_id(), layer_name)
        for ann in anns:
            self.add_new_ann(new_layer, ann)
        return new_layer

    def update_layer(self, layer, anns):
        self._inc_layer_revision(layer)
        for local_id, ann in anns:
            if local_id:
                uuid = self.local_id_manager.maps[
                    layer["annotation_type"]
                ].get_global_id(local_id)
                if uuid:
                    for key, value in ann.items():
                        layer["annotations"][uuid][key] = value
            # Local_id missing, possible cases
            # 1. New Annotation created
            # 2. Local_id gets deleted
            else:
                self.add_new_ann(layer, ann)
                # TODO: implement case 2

    def format_layer(self):
        old_layers = self.get_old_layers(self.layers)
        self.local_id_manager = LocalIdManager(old_layers)

        cross_vol_anns, non_cross_vol_anns = [], []
        for layer_name, layer_anns in self.layers.items():
            if layer_name in ["topic", "sub_topic"]:
                cross_vol_anns.append((layer_name, layer_anns))
            else:
                non_cross_vol_anns.append((layer_name, layer_anns))

        del self.layers

        # Create Annotaion layers
        for (i, vol_layers) in enumerate(zip(*non_cross_vol_anns)):
            base_id = f"v{i+1:03}"

            result = {}

            layer_name, layer_anns = vol_layers
            if layer_name not in old_layers:
                result[layer_name] = self.create_new_layer(layer_name, layer_anns)
            else:
                old_layer = old_layers[layer_name]
                self.update_layer(old_layer, layer_anns)
                result[layer_name] = old_layer

            yield result, base_id

        # Create Index layer
        Index_layer = Layer(self.get_unique_id(), "index")
        # loop over each topic
        for topic, sub_topic in zip(*cross_vol_anns):
            Topic = deepcopy(Text)
            Topic["id"] = self.get_unique_id()

            # loop over each sub_topic
            for corss_sub_topic in sub_topic:
                sub_text = deepcopy(SubText)
                sub_text["id"] = self.get_unique_id()
                for start, end, vol_id, work in corss_sub_topic:
                    sub_text["work"] = work
                    cross_vol_span = deepcopy(CrossVolSpan)
                    cross_vol_span["vol"] = f"base/v{vol_id:03}"
                    cross_vol_span["span"]["start"] = start
                    cross_vol_span["span"]["end"] = end
                    sub_text["span"].append(cross_vol_span)

                if corss_sub_topic:
                    Topic["parts"].append(sub_text)

            for start, end, vol_id, work in topic:
                Topic["work"] = work
                cross_vol_span = deepcopy(CrossVolSpan)
                cross_vol_span["vol"] = f"base/v{vol_id:03}"
                cross_vol_span["span"]["start"] = start
                cross_vol_span["span"]["end"] = end
                Topic["span"].append(cross_vol_span)

            Index_layer["annotations"].append(Topic)

        result = {"index": Index_layer}

        yield result, None

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

    def parse_ann(self, m_text, base_id):
        # Find start and end of annotation separately
        # TODO: apply multiprocessing on patterns
        start_markers, end_markers = [], []
        for ann_name, ann_value in self.config["ann_patterns"].items():
            start_markers.extend(self.get_markers(ann_name, ann_value["start"], m_text))
            end_markers.extend(self.get_markers(ann_name, ann_value["end"], m_text))

        # Sort all_starts and all_ends sperately
        start_markers = sort_by_pos(start_markers)
        ends_markers = sort_by_pos(end_markers)

        # Find ann_start and ann_end pair
        s_idx, e_idx = 0, 0
        offset = 0
        while s_idx < len(start_markers) or e_idx < len(end_markers):
            #         import pdb; pdb.set_trace()
            payload = 0
            ann_name, start_match = start_markers[s_idx]
            _, end_match = end_markers[e_idx]
            base_start, offset = get_base_idx(start_match, offset)

            # ann which includes text
            if self.config["ann_patterns"][ann_name]["has_text"]:
                # ann with payload
                if self.config["ann_patterns"][ann_name]["has_payload"]:
                    payload = get_payload(ann_name, start_match, end_match, m_text)
                    payload_len = (
                        len(payload)
                        + self.config["ann_patterns"][ann_name]["payload_sep_len"]
                    )
                base_end, offset = get_base_idx(
                    end_match, offset, is_end=True, payload_len=payload_len
                )

                self.layers[ann_name][base_id].append((base_start, base_end, payload))
            # ann which doesn't includes text
            else:
                # ann with payload
                if self.config["ann_patterns"][ann_name]["has_payload"]:
                    payload = get_payload(ann_name, start_match, end_match, m_text)
                _, offset = get_base_idx(
                    end_match, offset, is_end=True, payload_len=len(payload)
                )
                self.layers[ann_name][base_id].append((base_start, None, payload))

            s_idx += 1
            e_idx += 1

    def get_base_text(self):
        base_text = self.base_text.strip()
        self.base_text = ""

        return base_text

    def create_opf(self, input_path, **kwargs):
        input_path = Path(input_path)
        self._build_dirs(input_path)
        (self.dirs["opf_path"] / "base").mkdir(exist_ok=True)

        for i, (m_text, vol_name, n_vol) in enumerate(self.get_input(input_path)):
            print(f"[INFO] Processing Vol {i+1:03} of {n_vol}: {vol_name} ...")
            base_id = f"v{i+1:03}"
            self.build_layers(m_text, base_id)
            # save base_text
            # if (self.dirs['opf_path']/'base'/f'{base_id}.txt').is_file(): continue
            if "is_text" in kwargs:
                if kwargs["is_text"]:
                    continue

            base_text = self.get_base_text()
            (self.dirs["opf_path"] / "base" / f"{base_id}.txt").write_text(base_text)

        # save pecha layers
        layers = self.get_result()
        for vol_layers, base_id in self.format_layer(layers):
            if base_id:
                print(f"[INFO] Creating layers for {base_id} ...")
                vol_layer_path = self.dirs["layers_path"] / base_id
                vol_layer_path.mkdir(exist_ok=True)
            else:
                print("[INFO] Creating index layer for Pecha ...")

            for layer, ann in vol_layers.items():
                if layer == "index":
                    layer_fn = self.dirs["opf_path"] / f"{layer}.yml"
                else:
                    layer_fn = vol_layer_path / f"{layer}.yml"
                self.dump(ann, layer_fn)


class HFMLTextFromatter(HFMLFormatter):
    def __init_(self, output_path="./output", is_book=False):
        super().__init__(output_path=output_path, is_book=is_book)
        self.text_id = None

    def get_input(self, input_path):
        mtext = input_path.read_text()
        if self.is_book:
            return (self.text_preprocess(mtext), "Book", 1)

        vol_pattern = r"\[v\d{3}\]"
        cur_vol_text = ""
        vol_text = []
        vol_info = []
        vol_walker = 0
        lines = mtext.splitlines()
        n_line = len(lines)
        self.text_id = re.search(r"\{\w+\}", mtext)[0]
        for idx, line in enumerate(lines):
            vol_pat = re.search(vol_pattern, line)
            if vol_pat:
                vol_info.append(vol_pat[0][1:-1])
                if vol_walker > 0:
                    vol_text.append(cur_vol_text)
                    cur_vol_text = ""
                vol_walker += 1
            else:
                cur_vol_text += line + "\n"
            if idx == n_line - 1:
                vol_text.append(cur_vol_text)
                cur_vol_text = ""

        result = []
        for i, vol_id in enumerate(vol_info):
            result.append((self.text_preprocess(vol_text[i]), vol_id, vol_walker))
        return result

    def __adapt_span_to_vol(self, extra, vol_walker):
        """ It adapts the index of parse output of serilized hfml file of a particular text id.

        Agrs:
            extra (int): start of text Id span which needs to be added to all the index of annotation present in that text id.
            vol_walker (int): Adapts all the annotation which contains volume information.
        """

        first_vol = []
        if self.poti_title[0]:
            start = self.poti_title[0][0] + extra
            end = self.poti_title[0][1] + extra
            first_vol.append((start, end))
            first_vol.append(self.poti_title[1:])
            self.poti_title = first_vol
            first_vol = []
        if self.chapter_title[0]:
            start = self.chapter_title[0][0] + extra
            end = self.chapter_title[0][1] + extra
            first_vol.append((start, end))
            first_vol.append(self.chapter_title[1:])
            self.poti_title = first_vol
            first_vol = []
        if self.citation_pattern[0]:
            for cit in self.citation_pattern[0]:
                start = cit[0] + extra
                end = cit[1] + extra
                first_vol.append((start, end))
            self.citation_pattern[0] = first_vol
            first_vol = []
        if self.sabche_pattern[0]:
            for sabche in self.sabche_pattern[0]:
                start = sabche[0] + extra
                end = sabche[1] + extra
                first_vol.append((start, end))
            self.sabche_pattern[0] = first_vol
            first_vol = []
        if self.yigchung_pattern[0]:
            for yig in self.yigchung_pattern[0]:
                start = yig[0] + extra
                end = yig[1] + extra
                first_vol.append((start, end))
            self.yigchung_pattern[0] = first_vol
            first_vol = []
        if self.tsawa_pattern[0]:
            for tsawa in self.tsawa_pattern[0]:
                start = tsawa[0] + extra
                end = tsawa[1] + extra
                first_vol.append((start, end))
            self.tsawa_pattern[0] = first_vol
            first_vol = []
        if self.error_id[0]:
            for cor in self.error_id[0]:
                start = cor[0] + extra
                end = cor[1] + extra
                first_vol.append((start, end, cor[2]))
            self.error_id[0] = first_vol
            first_vol = []
        if self.notes_id[0]:
            for cor in self.notes_id[0]:
                start = cor[0] + extra
                first_vol.append(start)
            self.notes_id[0] = first_vol
            first_vol = []
        if self.abs_er_id[0]:
            for er in self.abs_er_id[0]:
                start = er[0] + extra
                end = er[1] + extra
                first_vol.append((start, end))
            self.abs_er_id[0] = first_vol
            first_vol = []
        if self.page[0]:
            for pg in self.page[0]:
                start = pg[0] + extra
                end = pg[1] + extra
                first_vol.append((start, end, pg[2], pg[3]))
            self.page[0] = first_vol
            first_vol = []

        if self.topic_id:
            cur_top = []
            for cur_vol_top in self.topic_id[0]:
                start = cur_vol_top[0]
                end = cur_vol_top[1]
                if cur_vol_top[2] == 1:
                    start += extra
                    end += extra
                cur_top.append(
                    (start, end, cur_vol_top[2] + vol_walker, cur_vol_top[3])
                )
            self.topic_id[0] = cur_top

        if self.sub_topic[0][0]:
            cur_topic = []
            for st in self.sub_topic[0][0]:
                cur_sub_top = []
                for cst in st:
                    start = cst[0]
                    end = cst[1]
                    if cst[2] == 1:
                        start += extra
                        end += extra
                    cur_sub_top.append((start, end, t[2] + vol_walker, t[3]))
                cur_topic.append(cur_sub_top)
            self.sub_topic[0] = cur_topic

    def get_result(self):
        index = self.load(self.dirs["opf_path"] / "index.yml")
        extra = 0
        for i, ann in enumerate(index["annotations"]):
            if ann["work"] == self.text_id:
                extra = ann["work"]["span"][0]["vol"]["span"]["start"]
                break
        if not self.is_book:
            self.__adapt_span_to_vol(extra, i)

        result = {
            "pecha_title": self.poti_title,
            "chapter_title": self.chapter_title,
            "citation": self.citation_pattern,
            "pagination": self.page,  # page variable format (start_index,end_index,pg_Info,pg_ann)
            "topic": self.topic_id,
            "sub_topic": self.sub_topic,
            "sabche": self.sabche_pattern,
            "tsawa": self.tsawa_pattern,
            "yigchung": self.yigchung_pattern,
            "correction": self.error_id,
            "error_candidate": self.abs_er_id,
            "peydurma": self.notes_id,
        }

        return result


if __name__ == "__main__":
    formatter = HFMLFormatter()
    formatter.create_opf("./tests/data/formatter/hfml/P000002/")

    formatter = HFMLTextFromatter()
    formatter.new_poti("./tests/data/formatter/hfml/vol_sep_test")
