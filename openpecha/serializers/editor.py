import re

from openpecha.core.layer import LayersEnum

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
    yigchung_SP = '<span class="yigchung"'
    footnote_marker_SP = '<span class="tibetan-footnote-marker"'
    footnote_EP = "</span></a>"
    footnote_reference_SP = '<span class="tibetan-footnote-reference"'


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
        start_payload = ""
        end_payload = ""
        ann_id = ann["id"]
        if ann["type"] == LayersEnum.correction.value:
            start_payload = "("
            end_payload = f',{ann["correction"]})'
        elif ann["type"] == LayersEnum.peydurma.value:
            start_payload = "#"
            only_start_ann = True
        elif ann["type"] == LayersEnum.error_candidate.value:
            start_payload = "["
            end_payload = "]"
        elif ann["type"] == LayersEnum.book_title.value:
            start_payload = f'{AnnotationTemplate.book_title_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayersEnum.sub_title.value:
            start_payload = f'{AnnotationTemplate.sub_title_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayersEnum.book_number.value:
            start_payload = f'{AnnotationTemplate.book_number_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayersEnum.author.value:
            start_payload = f'{AnnotationTemplate.author_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayersEnum.chapter:
            start_payload = f'{AnnotationTemplate.chapter_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayersEnum.tsawa.value:
            start_payload = f'{AnnotationTemplate.tsawa_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayersEnum.citation.value:
            start_payload = f'{AnnotationTemplate.quatation__SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayersEnum.sabche.value:
            start_payload = f'{AnnotationTemplate.sabche_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayersEnum.yigchung.value:
            start_payload = f'{AnnotationTemplate.yigchung_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayersEnum.footnote.value:
            start_payload = f'<a href="#fr{ann_id}>{AnnotationTemplate.footnote_marker_SP} id="fm{ann_id}">'
            end_payload = AnnotationTemplate.footnote_EP

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def p_tag_adder(self, body_text):
        new_body_text = ""
        body_text = re.sub(r"\n</span>", "\n</span>\n", body_text)
        paras = body_text.split("\n")
        para_flag = False
        cur_para = ""
        cur_span_payload = ""
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

    def serialize(self):
        self.apply_layers()
        self.layers = [layer for layer in self.layers if layer != "Pagination"]

        results = self.get_result()
        for base_name, result in results.items():
            result = self.p_tag_adder(result)
            yield base_name, result
