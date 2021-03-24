import os
import re
from pathlib import Path

import requests
import yaml

from openpecha.formatters.layers import AnnType

from .serialize import Serialize


class AnnotationTemplate:
    span_EP = "</span>"
    para_EP = "</p>"
    book_title_SP = '<p><span class="book-title"'
    sub_title_SP = '<p><span class="sub-title"'
    book_number_SP = '<p><span class="book-number"'
    author_SP = '<p><span class="author"'
    chapter_SP = '<p><span class="chapter"'
    tsawa_SP = '<span class="root-text"'
    quatation__SP = '<span class="citation"'
    sabche_SP = '<span class="sabche"'
    yigchung_SP = '<span class="yigchung">'
    footnote_marker_SP = '<span class="footnote-marker"'
    footnote_EP = "</span></a>"
    footnote_reference_SP = '<span class="footnote-reference"'


class EditorSerializer(Serialize):
    def __get_adapted_span(self, span, vol_id):
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
        adapted_start = span["start"] - self.text_spans[vol_id]["start"]
        adapted_end = span["end"] - self.text_spans[vol_id]["start"]
        return adapted_start, adapted_end

    def apply_annotation(self, vol_id, ann, uuid2localid):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            vol_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        only_start_ann = False
        start_payload = "("
        end_payload = ")"
        ann_id = ann["id"]
        if ann["type"] == AnnType.correction:
            start_payload = "("
            end_payload = f',{ann["correction"]})'
        elif ann["type"] == AnnType.peydurma:
            start_payload = "#"
            only_start_ann = True
        elif ann["type"] == AnnType.error_candidate:
            start_payload = "["
            end_payload = "]"
        elif ann["type"] == AnnType.book_title:
            start_payload = f'{AnnotationTemplate.book_title_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == AnnType.sub_title:
            start_payload = f'{AnnotationTemplate.sub_title_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == AnnType.book_number:
            start_payload = f'{AnnotationTemplate.book_number_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == AnnType.author:
            start_payload = f'{AnnotationTemplate.author_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == AnnType.chapter:
            start_payload = f'{AnnotationTemplate.chapter_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == AnnType.tsawa:
            start_payload = f'{AnnotationTemplate.tsawa_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == AnnType.citation:
            start_payload = f'{AnnotationTemplate.quatation__SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == AnnType.sabche:
            start_payload = f'{AnnotationTemplate.sabche_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == AnnType.yigchung:
            start_payload = f'{AnnotationTemplate.yigchung_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == AnnType.footnote:
            start_payload = f'<a href="#fr{ann_id}>{AnnotationTemplate.footnote_marker_SP} id="fm{ann_id}">'
            end_payload = AnnotationTemplate.footnote_EP

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def get_footnote_references(self, footnotes):
        footnote_references = ""
        for footnote_id, footnote in footnotes.items():
            footnote_references += f'<p><a href="#fm{footnote_id}">{AnnotationTemplate.footnote_reference_SP} id="fr{footnote_id}">{footnote["footnote_ref"]}</span></a></p>'
        return footnote_references

    def p_tag_adder(self, body_text):
        new_body_text = ""
        body_text = re.sub(r"\n</span>", "\n</span>\n", body_text)
        paras = body_text.split("\n")
        para_flag = False
        cur_para = ""
        for para in paras:
            if "<p" not in para:
                if re.search("<span.+?</span>", para):
                    new_body_text += f"<p>{para}</p>"
                elif "<span" in para and not para_flag:
                    cur_span_payload = re.search("<span .+>", para)[0]
                    cur_para += f"<p>{para}<br>"
                    para_flag = True
                elif para_flag and "</span>" not in para:
                    cur_para += f"{cur_span_payload}{para}</br>"
                elif "</span>" in para:
                    cur_para += f"{cur_span_payload}{para}</p>"
                    new_body_text += cur_para
                    cur_para = ""
                    para_flag = False
                    cur_span_payload = ""
                else:
                    new_body_text += f"<p>{para}</p>"
            else:
                new_body_text += para
        return new_body_text

    def serialize(self, output_path="./"):
        self.apply_layers()
        self.layers = [layer for layer in self.layers if layer != "Pagination"]

        results = self.get_result()
        for vol_id, result in results.items():
            footnote_ref_tag = ""
            if "Footnote" in self.layers:
                footnote_fn = self.opf_path / "layers" / vol_id / "Footnote.yml"
                footnote_layer = yaml.safe_load(footnote_fn.open())
                footnote_ref_tag = self.get_footnote_references(
                    footnote_layer["annotations"]
                )
            result = self.p_tag_adder(result)
            result = f"<html>\n<head>\n\t<title></title>\n</head>\n<body>\n{result}{footnote_ref_tag}</body>\n</html>"
            Path(f"{output_path}/{vol_id}.txt").write_text(result, encoding="utf-8")
