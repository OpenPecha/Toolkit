import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from openpecha.formatters.layers import AnnType

from .serialize import Serialize


class Tsadra_template:
    """Variables are important components of tsadra epub template."""

    # SP = Start_Payload
    span_EP = "</span>"
    para_EP = "</p>"
    ft = '<span class="front-title">'
    book_title_SP = '<p class="credits-page_front-title"><span class="front-title">'
    author_SP = '<p class="credits-page_front-page---text-author"><span class="front-page---text-titles">'
    chapter_SP = '<span class="tibetan-chapter1">'
    tsawa_SP = '<span class="tibetan-root-text">'
    tsawa_verse_SP = '<span class="tibetan-root-text_tibetan-root-text-middle-lines tibetan-root-text">'
    quatation__verse_SP = (
        '<span class="tibetan-citations-in-verse_tibetan-citations-middle-lines">'
    )
    quatation__SP = '<span class="tibetan-external-citations">'
    sabche_SP = '<span class="tibetan-sabche1">'
    yigchung_SP = '<span class="tibetan-commentary-small">'


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
        if ann["type"] == AnnType.pagination:
            start_payload = f'[{ann["page_index"]}] {ann["page_info"]}\n'
            only_start_ann = True
        elif ann["type"] == AnnType.correction:
            start_payload = "("
            end_payload = f',{ann["correction"]})'
        elif ann["type"] == AnnType.peydurma:
            start_payload = "#"
            only_start_ann = True
        elif ann["type"] == AnnType.error_candidate:
            start_payload = "["
            end_payload = "]"
        elif ann["type"] == AnnType.book_title:
            start_payload = Tsadra_template.book_title_SP
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
                    start_payload = Tsadra_template.quatation_verse_SP
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

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def serialize(self, output_path="./output/epub_output"):
        """ This module serialize .opf file to other format such as .epub etc. In case of epub,
        we are using calibre ebook-convert command to do the conversion by passing our custom css template
        and embedding our custom font. The converted output will be then saved in current directory
        as {pecha_id}.epub.

        Args:
        pecha_id (string): Pecha id that needs to be exported in other format

        """
        pecha_id = self.opfpath.name.split(".")[0]
        out_fn = f"{pecha_id}.html"
        try:
            pecha_title = self.meta["ebook_metadata"]["title"]
        except KeyError:
            pecha_title = ""
        try:
            cover_image = self.meta["ebook_metadata"]["cover"]
        except KeyError:
            cover_image = ""
        results = self.get_result()
        for vol_id, result in results.items():
            result = result.replace("\n", "<br>\n")
            results = (
                f"<html>\n<head>\n\t<title>{pecha_title}</title>\n</head>\n<body>\n"
            )
            results += f"{result}</body>\n</html>"
            Path(out_fn).write_text(results)
            # Downloading css template file from ebook template repo and saving it
            template = requests.get(
                "https://raw.githubusercontent.com/OpenPecha/ebook-template/master/tsadra_template.css"
            )
            Path("template.css").write_bytes(template.content)
            # click.echo(template.content, file=open('template.css', 'w'))
            # Running ebook-convert command to convert html file to .epub (From calibre)
            # XPath expression to detect chapter titles.
            chapter_Xpath = "//*[@class='tibetan-chapter']"
            font_family = "Monlam Uni Ouchan2"
            font_size = 15
            chapter_mark = "pagebreak"
            cover_path = self.opfpath / f"asset/image/{cover_image}"
            os.system(
                f'ebook-convert {out_fn} {output_path}/{pecha_id}.epub --extra-css=./template.css --chapter={chapter_Xpath} --chapter-mark="{chapter_mark}" --base-font-size={font_size} --embed-font-family="{font_family}" --cover={cover_path}'
            )
            # Removing html file and template file
            os.system(f"rm {out_fn}")
            os.system("rm template.css")
