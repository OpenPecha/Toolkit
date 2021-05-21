from collections import defaultdict
from typing import Dict

from bs4 import BeautifulSoup

from openpecha.core.annotation import AnnBase, Span, VerseTypeAnn
from openpecha.core.layer import Layer, LayerEnum


class EditorParser:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.layers: Dict[str, Dict[str, Layer]] = defaultdict(dict)
        self.base: Dict[str, str] = {}
        self.last_base_char_idx = -1

    def _add_base(self, root, base_name):
        self.base[base_name] = root.text

    def _get_content_span(self, text):
        start = self.last_base_char_idx + 1
        end = start + len(text) - 1
        self.last_base_char_idx = end
        return start, end

    def _get_ann(self, tag):
        start, end = self._get_content_span(tag.text)
        span = Span(start=start, end=end)
        return AnnBase(span=span), tag["id"]

    @staticmethod
    def _get_empty_layer(layerEnum):
        return Layer(annotation_type=layerEnum, revision="0000", annotations={})

    def _get_layer(self, base_name, layerEnum):
        layer = self.layers[base_name].get(layerEnum, self._get_empty_layer(layerEnum))
        self.layers[base_name][layerEnum] = layer
        return layer

    def _add_ann(self, base_name, layerEnum, tag):
        ann, id_ = self._get_ann(tag)
        layer = self._get_layer(base_name, layerEnum)
        layer.annotations[id_] = ann

    def __handle_non_ann(self, text):
        start, end = self._get_content_span(text)

    def _parse_p_tag(self, base_name, p):
        for child in p.children:
            if isinstance(child, str):
                self.__handle_non_ann(child)
                continue

            tag_class = child["class"]
            if "book-title" in tag_class:
                self._add_ann(base_name, LayerEnum.book_title, child)
            elif "sub-title" in tag_class:
                self._add_ann(base_name, LayerEnum.sub_title, child)
            elif "book-number" in tag_class:
                self._add_ann(base_name, LayerEnum.book_number, child)
            elif "author" in tag_class:
                self._add_ann(base_name, LayerEnum.author, child)
            elif "chapter" in tag_class:
                self._add_ann(base_name, LayerEnum.chapter, child)
            elif "citation" in tag_class:
                self._add_ann(base_name, LayerEnum.citation, child)
            elif "root-text" in tag_class:
                self._add_ann(base_name, LayerEnum.tsawa, child)
            elif "sabche" in tag_class:
                self._add_ann(base_name, LayerEnum.sabche, child)
            elif "yigchung" in tag_class:
                self._add_ann(base_name, LayerEnum.yigchung, child)

        # newline at the end of every p tag
        self.last_base_char_idx += 1

    def _group_anns(self, base_name, layer_name):
        def _create_ann(start, end, is_verse):
            return VerseTypeAnn(span=Span(start=start, end=end), is_verse=is_verse)

        if layer_name not in self.layers[base_name]:
            return

        layer = self.layers[base_name][layer_name]
        grouped_anns = {}

        # init with first ann
        anns = list(layer.annotations.items())
        true_id = anns[0][0]
        true_start = anns[0][1].span.start
        true_end = anns[0][1].span.end
        is_verse = False
        grouped_anns[true_id] = _create_ann(true_start, true_end, is_verse)

        for i, (id_, ann) in enumerate(anns[1:], start=2):

            # find the last element of the group
            if ann.span.start == (true_end + 2):
                true_end = ann.span.end
                is_verse = True
                if i == len(anns):
                    grouped_anns[true_id] = _create_ann(true_start, true_end, is_verse)

            # create the group
            elif i == len(anns) or ann.span.start > (true_end + 2):
                grouped_anns[true_id] = _create_ann(true_start, true_end, is_verse)

                # start next group with first element
                true_id = id_
                true_start = ann.span.start
                true_end = ann.span.end
                is_verse = False

                # single last ann
                if i == len(anns):
                    grouped_anns[true_id] = _create_ann(true_start, true_end, is_verse)

        layer.annotations = grouped_anns

    def parse(self, base_name, html, group=True):
        self._reset()

        root = BeautifulSoup(html, "html.parser")
        self._add_base(root, base_name)

        for p in root.find_all("p"):
            self._parse_p_tag(base_name, p)

        if group:
            self._group_anns(base_name, LayerEnum("Tsawa"))
            self._group_anns(base_name, LayerEnum("Citation"))
