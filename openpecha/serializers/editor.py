import re

from openpecha.core.layer import LayerEnum
from openpecha.utils import load_yaml

from .serialize import Serialize
from .epub import TsadraTemplateCSSClasses


class AnnotationTemplate:
    span_EP = "</span>"
    para_EP = "</p>"
    book_title_SP = '<p><span class="book-title"'
    sub_title_SP = '<p><span class="sub-title"'
    book_number_SP = '<p><span class="book-number"'
    author_SP = '<p><span class="author"'
    chapter_SP = '<p><span class="chapter"'
    tsawa_SP = '<span class="root-text"'
    tsawa_verse_SP = '<span class="root-text-verse"'
    citation_SP = '<span class="citation"'
    citation_verse_SP = '<span class="citation-verse"'
    citation_prose_SP = '<span class="citation-prose"'
    sabche_SP = '<span class="sabche"'
    yigchung_SP = '<span class="yigchung"'
    footnote_marker_SP = '<span class="footnote-marker"'
    footnote_EP = "</span></a>"
    footnote_reference_SP = '<span class="footnote-reference"'


class EditorSerializer(Serialize):
    def __get_adapted_span(self, span, base_id):
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
        adapted_start = span["start"] - self.text_spans[base_id]["start"]
        adapted_end = span["end"] - self.text_spans[base_id]["start"]
        return adapted_start, adapted_end

    def get_citation_sp(self, css_class_name, ann_id):
        """Return start payload for citation according to class name

        Args:
            css_class_name (str): css class name to differentiate different types of citations

        Returns:
            str: citation start payload
        """
        start_payload = f'{AnnotationTemplate.citation_SP} id="{ann_id}">'
        if css_class_name:
            css_class_enum = TsadraTemplateCSSClasses(css_class_name)
            if css_class_enum == TsadraTemplateCSSClasses.citation_verse:
                start_payload = f'{AnnotationTemplate.citation_verse_SP} id="{ann_id}">'
            elif css_class_enum == TsadraTemplateCSSClasses.citation_prose:
                start_payload = f'{AnnotationTemplate.citation_prose_SP} id="{ann_id}">'
        return start_payload


    def get_tsawa_sp(self, css_class_name, ann_id):
        """Return start payload for tsawa according to class name

        Args:
            css_class_name (str): css class name to differentiate different types of tsawa

        Returns:
            str: tsawa start payload
        """
        start_payload = f'{AnnotationTemplate.tsawa_SP} id="{ann_id}">'
        if css_class_name:
            css_class_enum = TsadraTemplateCSSClasses(css_class_name)
            if css_class_enum == TsadraTemplateCSSClasses.tsawa_verse:
                start_payload = f'{AnnotationTemplate.tsawa_verse_SP} id="{ann_id}">'
        return start_payload
        
    def apply_annotation(self, base_id, ann, uuid2localid):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            base_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        only_start_ann = False
        start_payload = ""
        end_payload = ""
        ann_id = ann["id"]
        if ann["type"] == LayerEnum.correction.value:
            start_payload = "("
            end_payload = f',{ann["correction"]})'
        elif ann["type"] == LayerEnum.peydurma.value:
            start_payload = "#"
            only_start_ann = True
        elif ann["type"] == LayerEnum.error_candidate.value:
            start_payload = "["
            end_payload = "]"
        elif ann["type"] == LayerEnum.book_title.value:
            start_payload = f'{AnnotationTemplate.book_title_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayerEnum.sub_title.value:
            start_payload = f'{AnnotationTemplate.sub_title_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayerEnum.book_number.value:
            start_payload = f'{AnnotationTemplate.book_number_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayerEnum.author.value:
            start_payload = f'{AnnotationTemplate.author_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayerEnum.chapter.value:
            start_payload = f'{AnnotationTemplate.chapter_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP + AnnotationTemplate.para_EP
        elif ann["type"] == LayerEnum.tsawa.value:
            css_class_name = self.get_css_class_name(ann)
            start_payload = self.get_tsawa_sp(css_class_name, ann_id)
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayerEnum.citation.value:
            css_class_name = self.get_css_class_name(ann)
            start_payload = self.get_citation_sp(css_class_name, ann_id)
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayerEnum.sabche.value:
            start_payload = f'{AnnotationTemplate.sabche_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayerEnum.yigchung.value:
            start_payload = f'{AnnotationTemplate.yigchung_SP} id="{ann_id}">'
            end_payload = AnnotationTemplate.span_EP
        elif ann["type"] == LayerEnum.footnote.value:
            start_payload = f'<a href="#fr{ann_id}>{AnnotationTemplate.footnote_marker_SP} id="fm{ann_id}">'
            end_payload = AnnotationTemplate.footnote_EP

        start_cc, end_cc = self.__get_adapted_span(ann["span"], base_id)
        self.add_chars(base_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(base_id, end_cc, False, end_payload)

    def get_footnote_references(self, footnotes):
        """Generate footnote references using footnote layer

        Args:
            footnotes (dict): footnote annotation information

        Returns:
            str: footnote references p tags
        """
        footnote_references = ""
        for footnote_id, footnote in footnotes.items():
            footnote_references += f'<p><a href="#fm{footnote_id}">{AnnotationTemplate.footnote_reference_SP} id="fr{footnote_id}">{footnote["footnote_ref"]}</span></a></p>'
        return footnote_references

    def p_tag_adder(self, body_text):
        """Add p tag to lines where it is missing

        Args:
            body_text (str): body tag of editor after layers are applied

        Returns:
            str: body tag with proper p tags
        """
        new_body_text = ""
        body_text = re.sub(r"\n</span>", "\n</span>\n", body_text)
        paras = body_text.split("\n")
        para_flag = False
        cur_para = ""
        id_walker = 1
        cur_span_payload = ""
        for para in paras:
            if "<p" not in para:
                if re.search("<span.+?</span>", para):
                    new_body_text += f"<p>{para}</p>"
                elif "<span" in para and not para_flag:
                    cur_span_payload = re.search("<span .+>", para)[0]
                    cur_para += f"<p>{para}</span></p>"
                    para_flag = True
                elif para_flag and "</span>" not in para:
                    cur_para += (
                        f'<p>{cur_span_payload[:-2]}{id_walker}">{para}</span></p>'
                    )
                    id_walker += 1
                elif "</span>" in para:
                    cur_para += f'<p>{cur_span_payload[:-2]}{id_walker}">{para}</p>'
                    new_body_text += cur_para
                    cur_para = ""
                    para_flag = False
                    cur_span_payload = ""
                    id_walker = 1
                else:
                    new_body_text += f"<p>{para}</p>"
            else:
                new_body_text += para
        return new_body_text

    def serialize(self):
        """Opf is serialize to html format in order to present it in editor workspace

        Yields:
            str, str: base file name, serialized html of that base file
        """
        self.apply_layers()
        self.layers = [layer for layer in self.layers if layer != "Pagination"]

        results = self.get_result()
        for base_name, result in results.items():
            footnote_ref_tag = ""
            if "Footnote" in self.layers:
                footnote_fn = self.opf_path / "layers" / base_name / "Footnote.yml"
                footnote_layer = load_yaml(footnote_fn)
                footnote_ref_tag = self.get_footnote_references(
                    footnote_layer["annotations"]
                )
            result = self.p_tag_adder(result)
            result = f"<html>\n<head>\n<title></title>\n</head>\n<body>\n{result}{footnote_ref_tag}</body>\n</html>"
            yield base_name, result
