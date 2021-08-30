from collections import defaultdict
from typing import Dict

from bs4 import BeautifulSoup
from pydantic.tools import T

from openpecha.core.annotation import AnnBase, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.serializers.epub import TsadraTemplateCSSClasses


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

    def _get_ann(self, tag, ann_class, extra_attrs):
        start, end = self._get_content_span(tag.text)
        span = Span(start=start, end=end)
        return ann_class(span=span, **extra_attrs), tag["id"]

    @staticmethod
    def _get_empty_layer(layerEnum):
        return Layer(annotation_type=layerEnum, revision="0000", annotations={})

    def _get_layer(self, base_name, layerEnum):
        layer = self.layers[base_name].get(layerEnum, self._get_empty_layer(layerEnum))
        self.layers[base_name][layerEnum] = layer
        return layer

    def _add_ann(self, base_name, layerEnum, tag, ann_class=AnnBase, extra_attrs={}):
        ann, id_ = self._get_ann(tag, ann_class, extra_attrs)
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
            elif "sabche" in tag_class:
                self._add_ann(base_name, LayerEnum.sabche, child)
            elif "yigchung" in tag_class:
                self._add_ann(base_name, LayerEnum.yigchung, child)
            elif "citation" in tag_class:
                self._add_ann(
                    base_name,
                    LayerEnum.citation,
                    child,
                    extra_attrs={
                        "metadata": {
                            "css_class_name": TsadraTemplateCSSClasses.citation_inline.value
                        }
                    },
                )
            elif "citation-verse" in tag_class:
                self._add_ann(
                    base_name,
                    LayerEnum.citation,
                    child,
                    extra_attrs={
                        "metadata": {
                            "css_class_name": TsadraTemplateCSSClasses.citation_verse.value
                        }
                    },
                )
            elif "citation-prose" in tag_class:
                self._add_ann(
                    base_name,
                    LayerEnum.citation,
                    child,
                    extra_attrs={
                        "metadata": {
                            "css_class_name": TsadraTemplateCSSClasses.citation_prose.value
                        }
                    },
                )
            elif "root-text" in tag_class:
                self._add_ann(
                    base_name,
                    LayerEnum.tsawa,
                    child,
                    extra_attrs={
                        "metadata": {
                            "css_class_name": TsadraTemplateCSSClasses.tsawa_inline.value
                        }
                    },
                )
            elif "root-text-verse" in tag_class:
                self._add_ann(
                    base_name,
                    LayerEnum.tsawa,
                    child,
                    extra_attrs={
                        "metadata": {
                            "css_class_name": TsadraTemplateCSSClasses.tsawa_verse.value
                        }
                    },
                )

        # newline at the end of every p tag
        self.last_base_char_idx += 1

    def _group_verse(self, base_name, layer_name):
        """Group same typed of annotation in consicutive order."""

        def _create_ann(start, end, is_verse):
            pass

        if layer_name not in self.layers[base_name]:
            return

        layer = self.layers[base_name][layer_name]
        verse_grouped_anns = {}

        anns = sorted(layer.annotations.items(), key=lambda ann: ann[1].span.start)

        verse_ended = True
        start_verse_ann_id = None
        prev_verse_ann = None
        for i, (ann_id, ann) in enumerate(anns):
            if "verse" in ann.metadata["css_class_name"]:
                if verse_ended:
                    verse_grouped_anns[ann_id] = ann
                    start_verse_ann_id = ann_id
                    verse_ended = False
                else:
                    prev_verse_ann = ann

                # if last ann is verse
                if i+1 == len(anns):
                    verse_grouped_anns[start_verse_ann_id].span.end = prev_verse_ann.span.end
            else:
                verse_grouped_anns[ann_id] = ann
                if not verse_ended:
                    verse_grouped_anns[start_verse_ann_id].span.end = prev_verse_ann.span.end
                    verse_ended = True

        layer.annotations = verse_grouped_anns


    def parse(self, base_name, html, group_verse=True):
        self._reset()

        root = BeautifulSoup(html, "html.parser")
        self._add_base(root, base_name)

        for p in root.find_all("p"):
            self._parse_p_tag(base_name, p)

        if group_verse:
            self._group_verse(base_name, LayerEnum("Tsawa"))
            self._group_verse(base_name, LayerEnum("Citation"))
