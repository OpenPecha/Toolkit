import re
from collections import defaultdict, namedtuple
from pathlib import Path

import requests
import yaml

from openpecha.formatters.layers import AnnType, SubText

INFO = "[INFO] {}"


class Serialize(object):
    """
    This class is used when serializing the .opf into anything else (Markdown, TEI, etc.).

    It is relatively abstract and needs to be inherited by a class doing an actual serialization.

    Note that currently we suppose that we're only adding characters, never removing any. This can
    change in the future but let's start simple.

    To use it, instantiate a concrete class with the path of the opf file, and call apply_layers() then get_result()
    """

    def __init__(
        self, opf_path, text_id=None, vol_ids=None, layers=None, index_layer=None
    ):
        self.opf_path = Path(opf_path)
        self.meta = self.get_meta_data()
        self.text_id = text_id
        self.index_layer = index_layer
        self.layers = layers
        self.n_char_shifted = []
        self.text_spans = {}
        self.base_layers = {}
        if self.text_id:
            self.text_spans = self.get_text_spans(text_id)
            self.index_layer = self.get_index_layer(text_id)
            if self.text_spans:
                self.base_layers = self.get_text_base_layer()
        else:
            if not vol_ids:
                vol_ids = [vol.stem for vol in (self.opf_path / "base").iterdir()]
            for vol_id in vol_ids:
                text_spans = {vol_id: {"start": 0, "end": float("inf")}}
                base_layers = {vol_id: self.get_base_layer(vol_id=vol_id)}
                self.text_spans.update(text_spans)
                self.base_layers.update(base_layers)
        """
        The chars_toapply is an important piece of the puzzle here. Basically applying the changes to the string directly is a
        bad idea for several reasons:
          - changing a big string with each annotation is costly
          - the application can be complex as character coordinate keep changing all the time

        So instead of just changing the string, we fill an object with all the characters we're going to add, then
        apply all the changes at once. This simplifies the code, the logic and is more efficient.

        The object has the following structure:

        {
            charcoord: (["string to apply before"],["string to apply after"])
        }

        So for example:
          Annotated text = XXXXXXXXX<title>TTTTTT</title>XXXXXXX
          - there is an annotation that goes from character 10 to character 15
          - the serialization you want to make is to add "<title>" before and "</title>" after the title
          - the chars_toapply object will be:

        {
            10: ([], ["<title>"]),
            15: (["</title>"], [])
        }
        """
        self.chars_toapply = defaultdict(dict)
        # layer lists the layers to be applied, in the order of which they should be applied
        # by convention, when it is None, all layers are applied in alphabetical order (?)

    def get_n_char_shitted(self, end):
        n_shifted = 0
        for pos, n_chars in self.n_char_shifted:
            if end >= pos:
                n_shifted += n_chars
        return n_shifted

    def _get_adapted_span(self, span, vol_id):
        """Adapts the annotation span to base-text of the text

        Adapts the annotation span, which is based on volume base-text
        to text base-text.

        Args:
            span (dict): span of a annotation, eg: {start:, end:}
            vol_id (str): id of vol, where part of the text exists.

        Returns:
            adapted_start (int): adapted start based on text base-text
            adapted_end (int): adapted end based on text base-text

        """
        adapted_start = max(0, span["start"] - self.text_spans[vol_id]["start"])
        adapted_end = span["end"] - self.text_spans[vol_id]["start"]
        n_char_shifted = self.get_n_char_shitted(span["start"])
        adapted_start += n_char_shifted
        adapted_end += n_char_shifted
        return adapted_start, adapted_end

    def get_meta_data(self):
        opf_path = self.opf_path
        try:
            meta = yaml.safe_load((opf_path / "meta.yml").open())
        except Exception:
            print("Meta data not Found!!!")
            meta = {}
        return meta

    def load_layer(self, fn):
        return yaml.safe_load(fn.open())

    def get_text_spans(self, text_id):
        """
        get spans of text
        """
        text_span = {}
        index_layer = self.load_layer(self.opf_path / "index.yml")
        for id, anno in index_layer["annotations"].items():
            if anno["parts"]:
                for sub_topic in anno["parts"]:
                    if sub_topic["work_id"] == text_id:
                        text_span[f'v{sub_topic["span"]["vol"]:03}'] = sub_topic["span"]
            if anno["work_id"] == text_id:
                for span in anno["span"]:
                    text_span[f'v{span["vol"]:03}'] = span
        return text_span

    def get_index_layer(self, text_id):
        index_layer = self.load_layer(self.opf_path / "index.yml")
        text_index_layer = defaultdict(str)
        text_index_layer["id"] = index_layer["id"]
        text_index_layer["annotation_type"] = index_layer["annotation_type"]
        text_index_layer["revision"] = index_layer["revision"]
        annotations = defaultdict(str)
        for id, anno in index_layer["annotations"].items():
            if anno["work_id"] == text_id:
                annotations[id] = anno
            elif anno["parts"]:
                annotation = {}
                annotation_span_list = []
                for sub_topic in anno["parts"]:
                    if sub_topic["work_id"] == text_id:
                        annotation["work_id"] = sub_topic["work_id"]
                        annotation_span_list.append(sub_topic["span"])
                        annotation["parts"] = []
                if annotation_span_list:
                    annotation["span"] = annotation_span_list
                    annotations[id] = annotation
        text_index_layer["annotations"] = annotations
        return text_index_layer

    def get_base_layer(self, vol_id=None):
        """
        return text for given span
        """
        if self.text_id:
            vol_base = (self.opf_path / f"base/{vol_id}.txt").read_text()
            start = self.text_spans[vol_id]["start"]
            end = self.text_spans[vol_id]["end"]
            return vol_base[start:end]
        else:
            vol_base = (self.opf_path / f"base/{vol_id}.txt").read_text()
            return vol_base

    def get_text_base_layer(self):
        """
        returns base text of text's volumes: dict

        for example:
        {
            'base/v005': text of given span of v001,
            ....
        }
        """
        base_layers = {}
        for vol_id in self.text_spans:
            base_layers[vol_id] = self.get_base_layer(vol_id)
        return base_layers

    def apply_layer(self, vol_id, layer_id):
        """
        This reads the file opfpath/layers/layer_id.yml and applies all the annotations it contains, in the order in which they appear.
        I think it can be implemented in this class by just calling self.apply_annotation on each annotation of the file.
        """
        layer_fn = self.opf_path / "layers" / vol_id / f"{layer_id}.yml"
        if not layer_fn.is_file():
            return
        layer = yaml.safe_load(layer_fn.open())
        for ann_id, ann in layer["annotations"].items():
            # text begins in middle of the page
            if (
                ann["span"]["end"] >= self.text_spans[vol_id]["start"]
                and ann["span"]["start"] <= self.text_spans[vol_id]["end"]
            ):
                ann["type"] = layer["annotation_type"]
                ann["id"] = ann_id
                try:
                    uuid2localid = layer["local_ids"]
                except Exception:
                    uuid2localid = ""
                self.apply_annotation(vol_id, ann, uuid2localid)

    def apply_index(self):
        for ann_id, topic in self.index_layer["annotations"].items():
            topic_ann = defaultdict(str)
            sub_topics = topic["parts"]
            for i, sub_topic in enumerate(sub_topics):
                if sub_topic:
                    vol_id = f"v{sub_topic['span']['vol']:03}"
                    sub_topic["type"] = AnnType.sub_topic
                    if sub_topic["work_id"] != sub_topics[i - 1]["work_id"]:
                        self.apply_annotation(vol_id, sub_topic)
            if topic["span"]:
                vol_id = f"v{topic['span'][0]['vol']:03}"
                topic_ann["type"] = AnnType.topic
                topic_ann["span"] = topic["span"][0]
                topic_ann["work_id"] = topic["work_id"]
                self.apply_annotation(vol_id, topic_ann)

    def get_all_layer(self, vol_id):
        """
        Returns all the layerid of layer from the layer directory
        """
        return [
            layer.stem
            for layer in (self.opf_path / "layers" / vol_id).iterdir()
            if layer.suffix == ".yml"
        ]

    def apply_layers(self):
        """
        This applies all the layers recorded in self.layers. If self.layers is none, it reads all the layers from the layer directory.
        """
        if not self.index_layer:
            index_path = self.opf_path / "index.yml"
            if index_path.is_file():
                self.index_layer = self.load_layer(index_path)
                self.apply_index()
        else:
            self.apply_index()
        for vol_id in self.base_layers:
            if not self.layers:
                self.layers = self.get_all_layer(vol_id)
            if "Pagination" in self.layers:
                pagination_index = self.layers.index("Pagination")
                del self.layers[pagination_index]
                self.layers.append("Pagination")
            for layer_id in self.layers:
                self.apply_layer(vol_id, layer_id)

    def add_chars(self, vol_id, cc, frombefore, charstoadd):
        """
        This records some characters to add at a character coordinate (cc), either frombefore (from the left) or after. before is a boolean.
        """
        if cc not in self.chars_toapply[vol_id]:
            self.chars_toapply[vol_id][cc] = ([], [])
        if frombefore:  # if from the left, layers should be applied in reverse order
            self.chars_toapply[vol_id][cc][0].insert(0, charstoadd)
        else:
            self.chars_toapply[vol_id][cc][1].append(charstoadd)

    def apply_annotation(self, vol_id, annotation):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            vol_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        raise NotImplementedError(
            "The Serialize class doesn't provide any serialization, please use a subclass such ass SerializeMd"
        )

    def _assign_line_layer(self, result, vol_id):
        def _get_page_index(line):
            page_index = ""
            if re.search("[𰵀-󴉱]", line):
                i = 2
            else:
                i = 1
            while line[i] != "]":
                page_index += line[i]
                i += 1
            return page_index

        result_with_line = ""
        page_index = ""
        n_line = 1
        for line in result.split("\n"):
            if re.search(r"\[[𰵀-󴉱]?[0-9]+[a-z]{1}\]", line):
                page_index = _get_page_index(line)
                n_line = 1
            elif not re.search(r"^\[", line):
                line = f"[{page_index}.{n_line}]" + line
                n_line += 1
            result_with_line += line + "\n"
        return result_with_line

    def get_result(self, line_num=True):
        """
        returns a string which is the base layer where the changes recorded in self.chars_toapply have been applied.

        The algorithm should be something like:
        """
        result = {}
        # don't actually do naive string concatenations
        # see https://waymoot.org/home/python_string/ where method 5 is good
        for vol_id, base_layer in self.base_layers.items():
            cur_vol_result = ""
            # if self.text_id:
            #     cur_vol_result += f"\n[{vol_id}]\n"
            i = 0
            for c in base_layer:
                # UTF bom \ufeff takes the 0th index
                if c == "\ufeff":
                    continue
                if i in self.chars_toapply[vol_id]:
                    apply = self.chars_toapply[vol_id][i]
                    for s in apply[0]:
                        cur_vol_result += s
                    cur_vol_result += c
                    for s in apply[1]:
                        cur_vol_result += s
                else:
                    cur_vol_result += c
                i += 1

            if "Pagination" in self.layers:
                cur_vol_result = self._assign_line_layer(cur_vol_result, vol_id)
            result.update({vol_id: cur_vol_result})
        return result
