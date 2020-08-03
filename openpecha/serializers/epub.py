import os
import requests

from .serialize import Serialize
from pathlib import Path
from openpecha.formatters.layers import AnnType


class Tsadra_template:
    """Variables are important components of tsadra epub template."""

    # SP = Start_Payload
    end_payload = "</span>"
    book_title_SP = '<span class="credits-page_front-title ">'
    author_SP = '<span class="credits-page_front-page---text-author">'
    chapter_SP = '<span class="tibetan-chapter">'
    tsawa_SP = '<span class="tibetan-root-text_tibetan-root-text-middle-lines">'
    quatation__verse_SP = (
        '<span class="tibetan-citations-in-verse_tibetan-citations-middle-lines">'
    )
    quatation__SP = '<span class="tibetan-external-citations">'
    sabche_SP = '<span class="tibetan-sabche">'
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

    def apply_annotation(self, vol_id, ann):
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
            end_payload = Tsadra_template.end_payload
        elif ann["type"] == AnnType.author:
            start_payload = Tsadra_template.author_SP
            end_payload = Tsadra_template.end_payload
        elif ann["type"] == AnnType.chapter:
            start_payload = Tsadra_template.chapter_SP
            end_payload = Tsadra_template.end_payload
        elif ann["type"] == AnnType.tsawa:
            start_payload = Tsadra_template.tsawa_SP
            end_payload = Tsadra_template.end_payload
        elif ann["type"] == AnnType.citation:
            if ann["isverse"]:
                start_payload = Tsadra_template.quatation_verse_SP
            else:
                start_payload = Tsadra_template.quatation__SP
            end_payload = Tsadra_template.end_payload
        elif ann["type"] == AnnType.sabche:
            start_payload = Tsadra_template.sabche_SP
            end_payload = Tsadra_template.end_payload
        elif ann["type"] == AnnType.yigchung:
            start_payload = Tsadra_template.yigchung_SP
            end_payload = Tsadra_template.end_payload

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def serilize(self, pecha_id):
        """ This module serialize .opf file to other format such as .epub etc. In case of epub,
        we are using calibre ebook-convert command to do the conversion by passing our custom css template
        and embedding our custom font. The converted output will be then saved in current directory
        as {pecha_id}.epub.

        Args:
        pecha_id (string): Pecha id that needs to be exported in other format

        """
        out_fn = f"{pecha_id}.html"
        # if self.meta['source_metadata']:
        #     pecha_title = self.meta['source_metadata']['title']
        # else:
        pecha_title = self.meta["ebook_metadata"]["title"]
        result, _ = self.get_result()
        result_lines = (
            result.splitlines()
        )  # Result is split where there is newline as we are going to consider newline as one para tag
        results = f"<html>\n<head>\n\t<title>{pecha_title}</title>\n</head>\n<body>\n"
        for result_line in result_lines:
            results += f'<p class="tibetan-regular-indented">{result_line}</p>\n'
        results += "</body>\n</html>"
        Path(out_fn).write_text(results)
        # Downloading css template file from ebook template repo and saving it
        template = requests.get(
            "https://raw.githubusercontent.com/OpenPecha/ebook-template/master/tsadra_template.css"
        )
        Path("template.css").write_bytes(template.content)
        # click.echo(template.content, file=open('template.css', 'w'))
        # Running ebook-convert command to convert html file to .epub (From calibre)
        chapter_Xpath = (
            "//*[@class='tibetan-chapter']"  # XPath expression to detect chapter titles.
        )
        font_family = "Monlam Uni Ouchan2"
        font_size = 16
        chapter_mark = "pagebreak"
        os.system(
            f'ebook-convert {out_fn} ./output/epub_output/{pecha_id}.epub --extra-css=./template.css --chapter={chapter_Xpath} --chapter-mark="{chapter_mark}" --base-font-size={font_size} --embed-font-family="{font_family}"'
        )
        # Removing html file and template file
        os.system(f"rm {out_fn}")
        os.system("rm template.css")
