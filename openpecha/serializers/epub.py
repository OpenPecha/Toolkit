import os
import re
from pathlib import Path

import requests
import yaml

from openpecha.formatters.layers import AnnType

from .serialize import Serialize


class Tsadra_template:
    """Variables are important components of tsadra epub template."""

    # SP = Start_Payload
    span_EP = "</span>"
    para_EP = "</p>"
    ft = '<span class="front-title">'
    cover_page_book_title_SP = '<span class="credits-page_front-title">'
    book_title_SP = '<span class="tibetan-book-title">'
    sub_title_SP = '<span class="tibetan-book-sub-title">'
    book_number_SP = f'<p class="tibetan-book-number">{ft}'
    credit_page_SP = (
        '<p class="credits-page_epub-edition-line"><span class="credits-regular">'
    )
    author_SP = '<p class="text-author"><span class="front-page---text-titles">'
    chapter_SP = '<span class="tibetan-chapters">'
    tsawa_SP = '<span class="tibetan-root-text">'
    tsawa_verse_SP = '<span class="tibetan-root-text-in-verse">'
    quatation__verse_SP = '<span class="tibetan-citations-in-verse">'
    quatation__SP = '<span class="tibetan-external-citations">'
    sabche_SP = '<span class="tibetan-sabche1">'
    yigchung_SP = '<span class="tibetan-commentary-small">'
    footnote_marker_SP = '<span class="tibetan-footnote-marker"'
    footnote_EP = "</span></a>"
    footnote_reference_SP = '<span class="tibetan-footnote-reference"'


class EpubSerializer(Serialize):
    """Epub serializer class for OpenPecha."""

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
        # if ann["type"] == AnnType.pagination:
        #     start_payload = f'[{ann["page_index"]}] {ann["page_info"]}\n'
        #     only_start_ann = True
        if ann["type"] == AnnType.correction:
            start_payload = "("
            end_payload = f',{ann["correction"]})'
        elif ann["type"] == AnnType.peydurma:
            start_payload = "#"
            only_start_ann = True
        elif ann["type"] == AnnType.credit_page:
            credit_page_ann = ann["credit_page_img_name"]
            start_payload = f'{Tsadra_template.credit_page_SP}<img src="{self.opf_path}/assets/image/{credit_page_ann}"/></span></p>\n'
            only_start_ann = True
        elif ann["type"] == AnnType.error_candidate:
            start_payload = "["
            end_payload = "]"
        elif ann["type"] == AnnType.book_title:
            start_payload = Tsadra_template.book_title_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.sub_title:
            start_payload = Tsadra_template.sub_title_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.book_number:
            start_payload = Tsadra_template.book_number_SP
            end_payload = f"{Tsadra_template.span_EP}{Tsadra_template.para_EP}"
        elif ann["type"] == AnnType.author:
            start_payload = Tsadra_template.author_SP
            end_payload = f"{Tsadra_template.span_EP}{Tsadra_template.para_EP}"
        elif ann["type"] == AnnType.chapter:
            start_payload = Tsadra_template.chapter_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.tsawa:
            try:
                if ann["isverse"]:
                    start_payload = Tsadra_template.tsawa_verse_SP
                else:
                    start_payload = Tsadra_template.tsawa_SP
            except Exception:
                start_payload = Tsadra_template.tsawa_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.citation:
            try:
                if ann["isverse"]:
                    start_payload = Tsadra_template.quatation__verse_SP
                else:
                    start_payload = Tsadra_template.quatation__SP
            except Exception:
                start_payload = Tsadra_template.quatation__SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.sabche:
            start_payload = Tsadra_template.sabche_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.yigchung:
            start_payload = Tsadra_template.yigchung_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.footnote:
            start_payload = f'<a href="#fr{ann["id"]}">{Tsadra_template.footnote_marker_SP} id="fm{ann["id"]}">'
            end_payload = Tsadra_template.footnote_EP

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
        for para in paras:
            if "<p" not in para:
                if re.search("<span.+?</span>", para):
                    new_body_text += f"<p>{para}</p>"
                elif "<span" in para and not para_flag:
                    cur_para += f"<p>{para}<br>"
                    para_flag = True
                elif para_flag and "</span>" not in para:
                    cur_para += f"{para}</br>"
                elif "</span>" in para:
                    cur_para += f"{para}</p>"
                    new_body_text += cur_para
                    cur_para = ""
                    para_flag = False
                else:
                    new_body_text += f"<p>{para}</p>"
            else:
                new_body_text += para
        return new_body_text

    def is_title(self, p_tag):
        if "title" in p_tag or "chapter" in p_tag or "number" in p_tag:
            return True
        else:
            return False

    def is_sabche_only(self, p_tag):
        if re.search('<p><span class="tibetan-sabche1">', p_tag):
            return True
        else:
            return False

    def rm_indentation(self, p_tag):
        if self.is_sabche_only(p_tag):
            p_tag = p_tag.replace(
                '<p><span class="tibetan-sabche1">', '<p><span class="tibetan-sabche">'
            )
        if len(self.get_p_text(p_tag)) > 50:
            p_tag = re.sub("<p>", '<p class="tibetan-commentary-non-indent">', p_tag)
        else:
            p_tag = p_tag.replace("<p>", '<p class="tibetan-regular-indented">')
        return p_tag

    def add_indentation(self, p_tag):
        p_tag = re.sub("<p>", '<p class="tibetan-regular-indented">', p_tag)
        return p_tag

    def is_annotated_p_tag(self, p_tag):
        if re.search("<p><span.*?>.+?</span></p>", p_tag) or re.search(
            '<p class=".+"><span class=".+">.+?</span></p>', p_tag
        ):
            return True
        else:
            return False

    def get_p_text(self, p_tag):
        para_tag = re.search(r"<p.*?>(<span.*?>)?(.+?)(</span>)?</p>", p_tag)
        para_text = para_tag.group(2)
        return para_text

    def get_p_tags(self, body_text):
        p_tags = re.split("(<p.*?>.+?</p>)", body_text)
        return p_tags[1::2]

    def has_yigchung(self, prev_p_tag):
        if Tsadra_template.yigchung_SP in prev_p_tag:
            return True
        else:
            return False

    def add_page_break(self, prev_p_tag, body_text):
        if not self.is_title(prev_p_tag) and (
            len(self.get_p_text(prev_p_tag)) > 500 or self.has_yigchung(prev_p_tag)
        ):
            new_prev_p_tag = prev_p_tag.replace(
                '<p class="tibetan-commentary-non-indent">',
                '<p class="tibetan-commentary-non-indent1">',
            )
            new_prev_p_tag = new_prev_p_tag.replace(
                '<p class="tibetan-regular-indented">',
                '<p class="tibetan-regular-indented1">',
            )
        else:
            new_prev_p_tag = prev_p_tag
        return body_text.replace(prev_p_tag, new_prev_p_tag)

    def indentation_adjustment(self, body_text):
        p_tags = self.get_p_tags(body_text)

        prev_p_tag = p_tags[0]
        body_text = prev_p_tag
        for p_tag in p_tags[1:]:
            cur_p_tag = ""
            if self.is_annotated_p_tag(prev_p_tag):
                if not self.is_title(p_tag):
                    cur_p_tag = self.rm_indentation(p_tag)
                else:
                    body_text = self.add_page_break(prev_p_tag, body_text)
                    cur_p_tag = self.add_indentation(p_tag)
            else:
                if self.is_annotated_p_tag(p_tag):
                    if not self.is_title(p_tag):
                        cur_p_tag = self.rm_indentation(p_tag)
                    else:
                        body_text = self.add_page_break(prev_p_tag, body_text)
                        cur_p_tag = self.add_indentation(p_tag)
                else:
                    if (
                        len(self.get_p_text(prev_p_tag)) < 50
                        and len(self.get_p_text(p_tag)) > 150
                    ):
                        cur_p_tag = p_tag.replace(
                            "<p>", '<p class="tibetan-commentary-non-indent">'
                        )
                    else:
                        cur_p_tag = self.add_indentation(p_tag)
            body_text += cur_p_tag
            prev_p_tag = cur_p_tag
        return body_text

    def get_footnote_references(self, footnotes):
        footnote_references = ""
        p_tag = '<p class = "tibetan-commentary-non-indent">'
        for footnote_id, footnote in footnotes.items():
            footnote_references += f'{p_tag}<a href="#fm{footnote_id}">{Tsadra_template.footnote_reference_SP} id="fr{footnote_id}">{footnote["footnote_ref"]}</span></a></p>'
        return footnote_references

    def serialize(self, toc_levels={}, output_path="./output/epub_output"):
        """This module serialize .opf file to other format such as .epub etc. In case of epub,
        we are using calibre ebook-convert command to do the conversion by passing our custom css template
        and embedding our custom font. The converted output will be then saved in current directory
        as {pecha_id}.epub.

        Args:
        pecha_id (string): Pecha id that needs to be exported in other format

        """
        output_path = Path(output_path)
        out_html_fn = f"{self.meta['id']}.html"
        pecha_title = self.meta["source_metadata"].get("title", "")
        cover_image = self.meta["source_metadata"].get("cover", "")

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
            result = self.indentation_adjustment(result)
            results = (
                f"<html>\n<head>\n\t<title>{pecha_title}</title>\n</head>\n<body>\n"
            )
            results += f"{result}{footnote_ref_tag}</body>\n</html>"
            Path(out_html_fn).write_text(results)
            # Downloading css template file from ebook template repo and saving it
            template = requests.get(
                "https://raw.githubusercontent.com/OpenPecha/ebook-template/master/tsadra_template.css"
            )
            Path("template.css").write_bytes(template.content)
            # Running ebook-convert command to convert html file to .epub (From calibre)
            # XPath expression to detect chapter titles.
            try:
                level1_toc_Xpath = toc_levels["1"]
                level2_toc_Xpath = toc_levels["2"]
                level3_toc_Xpath = toc_levels["3"]
            except Exception:
                level1_toc_Xpath = ""
                level2_toc_Xpath = ""
                level3_toc_Xpath = ""
            book_title_Xpath = "//*[@class='tibetan-book-title']"
            cover_path = self.opf_path / f"assets/image/{cover_image}"
            out_epub_fn = output_path / f"{self.meta['id']}.epub"
            font_family = "Monlam Uni Ouchan2"
            os.system(
                f'ebook-convert {out_html_fn} {out_epub_fn} --extra-css=./template.css --embed-font-family="{font_family}" --page-breaks-before="{book_title_Xpath}" --cover={cover_path} --flow-size=0 --level1-toc="{level1_toc_Xpath}" --level2-toc="{level2_toc_Xpath}" --level3-toc="{level3_toc_Xpath}" --use-auto-toc --disable-font-rescaling'
            )
            # Removing html file and template file
            os.system(f"rm {out_html_fn}")
            os.system("rm template.css")

            return out_epub_fn
