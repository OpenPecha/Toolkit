import re
from collections import defaultdict, namedtuple
from pathlib import Path

from openpecha.formatters.layers import AnnType, SubText
from openpecha.utils import load_yaml

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
        self, opf_path, text_id=None, base_ids=None, layers=None, index_layer=None
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
            self.text_spans = self.get_text_spans(text_id, index_layer)
            self.index_layer = self.get_index_layer(text_id, index_layer)
            if self.text_spans:
                self.base_layers = self.get_text_base_layer()
        else:
            if not base_ids:
                base_ids = [vol.stem for vol in (self.opf_path / "base").iterdir()]
            for base_id in base_ids:
                text_spans = {base_id: {"start": 0, "end": float("inf")}}
                base_layers = {base_id: self.get_base_layer(base_id=base_id)}
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

    def _get_adapted_span(self, span, base_id):
        """Adapts the annotation span to base-text of the text

        Adapts the annotation span, which is based on volume base-text
        to text base-text.

        Args:
            span (dict): span of a annotation, eg: {start:, end:}
            base_id (str): id of vol, where part of the text exists.

        Returns:
            adapted_start (int): adapted start based on text base-text
            adapted_end (int): adapted end based on text base-text

        """
        adapted_start = max(0, span["start"] - self.text_spans[base_id]["start"])
        adapted_end = span["end"] - self.text_spans[base_id]["start"]
        n_char_shifted = self.get_n_char_shitted(span["start"])
        adapted_start += n_char_shifted
        adapted_end += n_char_shifted
        return adapted_start, adapted_end

    def get_meta_data(self):
        opf_path = self.opf_path
        try:
            meta = load_yaml((opf_path / "meta.yml"))
        except Exception:
            print("Meta data not Found!!!")
            meta = {}
        return meta

    def get_css_class_name(self, annotation):
        """Return css class name of annotation if any exist

        Args:
            annotation (dict): annotation details

        Returns:
            str: css class name of the annotation
        """
        css_class_name = ""
        metadata = annotation.get("metadata", {})
        if metadata:
            css_class_name = metadata.get("css_class_name", "")
        return css_class_name

    def get_text_spans(self, text_id, index_layer):
        """
        get spans of text
        """
        text_span = {}
        if not index_layer:
            index_layer = load_yaml(self.opf_path / "index.yml")
        for id, anno in index_layer["annotations"].items():
            if anno["parts"]:
                for sub_topic in anno["parts"]:
                    if sub_topic["work_id"] == text_id:
                        text_span[f'{sub_topic["span"]["base"]}'] = sub_topic["span"]
            if anno["work_id"] == text_id:
                for span in anno["span"]:
                    text_span[f'{span["base"]}'] = span
        return text_span

    def get_index_layer(self, text_id, index_layer):
        if not index_layer:
            index_layer = load_yaml(self.opf_path / "index.yml")
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

    def get_base_layer(self, base_id=None):
        """
        return text for given span
        """
        if self.text_id:
            vol_base = (self.opf_path / f"base/{base_id}.txt").read_text()
            start = self.text_spans[base_id]["start"]
            end = self.text_spans[base_id]["end"]
            return vol_base[start : end + 1]
        else:
            vol_base = (self.opf_path / f"base/{base_id}.txt").read_text()
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
        for base_id in self.text_spans:
            base_layers[base_id] = self.get_base_layer(base_id)
        return base_layers

    def apply_layer(self, base_id, layer_id):
        """
        This reads the file opfpath/layers/layer_id.yml and applies all the annotations it contains, in the order in which they appear.
        I think it can be implemented in this class by just calling self.apply_annotation on each annotation of the file.
        """
        layer_fn = self.opf_path / "layers" / base_id / f"{layer_id}.yml"
        if not layer_fn.is_file():
            return
        layer = load_yaml(layer_fn)
        for ann_id, ann in layer["annotations"].items():
            # text begins in middle of the page
            if (
                ann["span"]["end"] >= self.text_spans[base_id]["start"]
                and ann["span"]["start"] <= self.text_spans[base_id]["end"]
            ):
                ann["type"] = layer["annotation_type"]
                ann["id"] = ann_id
                try:
                    uuid2localid = layer["local_ids"]
                except Exception:
                    uuid2localid = ""
                self.apply_annotation(base_id, ann, uuid2localid)

    def apply_index(self):
        for ann_id, topic in self.index_layer["annotations"].items():
            topic_ann = defaultdict(str)
            sub_topics = topic["parts"]
            for sub_topic_uuid, sub_topic in sub_topics.items():
                sub_topic_ann = defaultdict(str)
                base_id = sub_topic['span'][0]['base']
                sub_topic_ann["type"] = AnnType.sub_topic
                sub_topic_ann["work_id"] = sub_topic["work_id"]
                sub_topic_ann["span"] = sub_topic["span"][0]
                self.apply_annotation(base_id, sub_topic_ann)
            if topic["span"]:
                base_id = topic['span'][0]['base']
                topic_ann["type"] = AnnType.topic
                topic_ann["span"] = topic["span"][0]
                topic_ann["work_id"] = topic["work_id"]
                self.apply_annotation(base_id, topic_ann)

    def get_all_layer(self, base_id):
        """
        Returns all the layerid of layer from the layer directory
        """
        return [
            layer.stem
            for layer in (self.opf_path / "layers" / base_id).iterdir()
            if layer.suffix == ".yml"
        ]

    def apply_layers(self):
        """
        This applies all the layers recorded in self.layers. If self.layers is none, it reads all the layers from the layer directory.
        """
        if not self.index_layer:
            index_path = self.opf_path / "index.yml"
            if index_path.is_file():
                self.index_layer = load_yaml(index_path)
                self.apply_index()
        else:
            self.apply_index()
        for base_id in self.base_layers:
            if not self.layers:
                self.layers = self.get_all_layer(base_id)
            if "Pagination" in self.layers:
                pagination_index = self.layers.index("Pagination")
                del self.layers[pagination_index]
                self.layers.append("Pagination")
            for layer_id in self.layers:
                self.apply_layer(base_id, layer_id)

    def add_chars(self, base_id, cc, frombefore, charstoadd):
        """
        This records some characters to add at a character coordinate (cc), either frombefore (from the left) or after. before is a boolean.
        """
        if cc not in self.chars_toapply[base_id]:
            self.chars_toapply[base_id][cc] = ([], [])
        if frombefore:  # if from the left, layers should be applied in reverse order
            self.chars_toapply[base_id][cc][0].insert(0, charstoadd)
        else:
            self.chars_toapply[base_id][cc][1].append(charstoadd)

    def apply_annotation(self, base_id, annotation):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            base_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        raise NotImplementedError(
            "The Serialize class doesn't provide any serialization, please use a subclass such ass SerializeMd"
        )

    def _clip_extra_newline(self, cur_vol_result):
        """An extra line found in pages are removed.

        Args:
            cur_vol_result (str): serialized result without line annotation

        Returns:
            str: clean serialize results
        """
        clean_result = ""
        pages_and_anns = re.split(r"(〔[𰵀-󴉱]?\d+〕)", cur_vol_result)
        for page_and_ann in pages_and_anns:
            if page_and_ann:
                if re.search(r"\(([𰵀-󴉱])?\d+\)", page_and_ann):
                    clean_result += page_and_ann
                else:
                    if page_and_ann[-1] == "\n":
                        clean_result += page_and_ann[:-1]
                    else:
                        clean_result += page_and_ann
        return clean_result

    def get_result(self, line_num=True):
        """
        returns a string which is the base layer where the changes recorded in self.chars_toapply have been applied.

        The algorithm should be something like:
        """
        result = {}
        # don't actually do naive string concatenations
        # see https://waymoot.org/home/python_string/ where method 5 is good
        for base_id, base_layer in self.base_layers.items():
            cur_vol_result = ""
            # if self.text_id:
            #     cur_vol_result += f"\n[{base_id}]\n"
            i = 0
            for c in base_layer:
                # UTF bom \ufeff takes the 0th index
                if c == "\ufeff":
                    continue
                if i in self.chars_toapply[base_id]:
                    apply = self.chars_toapply[base_id][i]
                    for s in apply[0]:
                        cur_vol_result += s
                    cur_vol_result += c
                    for s in apply[1]:
                        cur_vol_result += s
                else:
                    cur_vol_result += c
                i += 1

            if "Pagination" in self.layers:
                cur_vol_result = self._clip_extra_newline(cur_vol_result)
            result.update({base_id: cur_vol_result})
        return result
