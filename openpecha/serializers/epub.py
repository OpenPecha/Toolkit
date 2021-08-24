import os
import re
import requests
import shutil
import zipfile

from bs4 import BeautifulSoup
from pathlib import Path

from openpecha.formatters.layers import AnnType
from openpecha.utils import load_yaml
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
    quatation__SP = '<span class="tibetan-citations">'
    sabche_SP = '<span class="tibetan-sabche1">'
    yigchung_SP = '<span class="tibetan-commentary-small">'
    footnote_marker_SP = '<span class="tibetan-footnote-marker"'
    footnote_EP = "</span></a>"
    footnote_reference_SP = '<span class="tibetan-footnote-reference"'

    toc_xpaths = {
        "book-number": "//*[@class='tibetan-book-number']",
        "chapter": "//*[@class='tibetan-chapters']",
        "sabche": "//*[@class='tibetan-sabche1' or @class='tibetan-sabche']",
    }
    toc_levels = {"1": "book-number", "2": "chapter", "3": "sabche"}
    book_title_Xpath = "//*[@class='tibetan-book-title']"


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
            if "is_verse" in ann and ann["is_verse"]:
                start_payload = Tsadra_template.tsawa_verse_SP
            else:
                start_payload = Tsadra_template.tsawa_SP
            end_payload = Tsadra_template.span_EP
        elif ann["type"] == AnnType.citation:
            if "is_verse" in ann and ann["is_verse"]:
                start_payload = Tsadra_template.quatation__verse_SP
            else:
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
        """Add p tag to lines where it is missing

        Args:
            body_text (str): body tag of ebook after layers are applied

        Returns:
            str: body tag with proper p tags
        """
        new_body_text = ""
        body_text = re.sub(r"\n</span>", "\n</span>\n", body_text)
        paras = body_text.split("\n")
        para_flag = False
        cur_span_payload = ""
        cur_para = ""
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
                        f'<p>{cur_span_payload[:-2]}-middle-line">{para}</span></p>'
                    )
                elif "</span>" in para:
                    cur_para += f'<p>{cur_span_payload[:-2]}-last-line">{para}</p>'
                    new_body_text += cur_para
                    cur_para = ""
                    para_flag = False
                    cur_span_payload = ""
                else:
                    new_body_text += f"<p>{para}</p>"
            else:
                new_body_text += para
        return new_body_text

    def is_title(self, p_tag):
        """Check if a p tag is title type annotation such as title, subtitle, chapter or book-number

        Args:
            p_tag (str): p tag of a body text

        Returns:
            boolean: True if p tag is title type annotation else False
        """
        if "title" in p_tag or "chapter" in p_tag or "number" in p_tag:
            return True
        else:
            return False

    def is_sabche_only(self, p_tag):
        """Check if p tag is non inline sabche or not

        Args:
            p_tag (str): p tag of a body text

        Returns:
            boolean: True if p tag is non inline sache else False
        """
        if re.search('<p><span class="tibetan-sabche1">', p_tag):
            return True
        else:
            return False

    def rm_indentation(self, p_tag):
        """Return p tag with non indented style

        Args:
            p_tag (str): p tag of a body text

        Returns:
            str: p tag with non indented style
        """
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
        """Add indentation style to p tag

        Args:
            p_tag (str): p tag of boody text

        Returns:
            str: p tag with indentation style
        """
        p_tag = re.sub("<p>", '<p class="tibetan-regular-indented">', p_tag)
        return p_tag

    def is_annotated_p_tag(self, p_tag):
        """Check a p tag is annotated p tag or not

        Args:
            p_tag (str): p tag of a body text

        Returns:
            boolean: True if p tag is annotated else False
        """
        if re.search("<p><span.*?>.+?</span></p>", p_tag) or re.search(
            '<p class=".+"><span class=".+">.+?</span></p>', p_tag
        ):
            return True
        else:
            return False

    def get_p_text(self, p_tag):
        """Return text included in p tag

        Args:
            p_tag (str): p tag of body text

        Returns:
            str: text of p tag
        """
        para_tag = re.search(r"<p.*?>(<span.*?>)?(.+?)(</span>)?</p>", p_tag)
        para_text = para_tag.group(2)
        return para_text

    def get_p_tags(self, body_text):
        """Return all the p tags in body text

        Args:
            body_text (str): body text of the ebook

        Returns:
            list: p tags in body text
        """
        p_tags = re.split("(<p.*?>.+?</p>)", body_text)
        return p_tags[1::2]

    def has_yigchung(self, p_tag):
        """Check if p tag contains yigchung or not

        Args:
            p_tag (str): p tag of a body

        Returns:
            boolean: True of yigchung exist in p tag else False
        """
        if Tsadra_template.yigchung_SP in p_tag:
            return True
        else:
            return False

    def get_front_page(self):
        """Construct the front page of the book including title, subtitle, authors and credit page

        Returns:
            str: front page content
        """
        front_page = ""
        source_metadata = self.meta.get("source_metadata", {})
        credit_pg_name = source_metadata.get("credit", "")
        credit_pg_path = self.opf_path / f"assets/image/{credit_pg_name}"
        book_title_tag = f'<p class="tibetan-regular-indented">{Tsadra_template.cover_page_book_title_SP}{source_metadata.get("title", "")}</span></p>\n'
        sub_title_tag = f'<p class="tibetan-regular-indented">{Tsadra_template.sub_title_SP}{source_metadata.get("subtitle", "")}</span></p>\n'
        authors = source_metadata.get("authors", [])
        front_page += f"{book_title_tag}{sub_title_tag}"
        for author in authors:
            front_page += f"{Tsadra_template.author_SP}{author}</span></p>\n"
        if credit_pg_path.is_file():
            front_page += f'{Tsadra_template.credit_page_SP}<img src="{self.opf_path}/assets/image/{credit_pg_name}" alt="credit image not found"/></span></p>\n'
        return front_page

    def add_page_break(self, prev_p_tag, body_text):
        """Add page break before title annotation type p tag

        Args:
            prev_p_tag (str): prev tag of the title type p tag
            body_text (str): body text of ebook

        Returns:
            str: body text with page break before title type p tag
        """
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
        """Add required indentation styles to body text's p tags

        Args:
            body_text (str): body of the ebook

        Returns:
            str: body text having p tags with expected indentation styles
        """
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
        """Generate footnote references using footnote layer

        Args:
            footnotes (dict): footnote annotation information

        Returns:
            str: footnote references p tags
        """
        footnote_references = ""
        p_tag = '<p class = "tibetan-commentary-non-indent">'
        for footnote_id, footnote in footnotes.items():
            footnote_references += f'{p_tag}<a href="#fm{footnote_id}">{Tsadra_template.footnote_reference_SP} id="fr{footnote_id}">{footnote["footnote_ref"]}</span></a></p>'
        return footnote_references

    def set_toc_level(self, toc_levels, serialized_html):
        """Return toc outline by checking presences of title type annotations and sabche

        Args:
            toc_levels (dict): toc level outline given by user
            serialized_html (str): final serialize html of the opf

        Returns:
            dict: toc outline created using existing title type annotations or sabche
        """
        new_toc_levels = {}
        walker = 1
        for level, annotation_name in toc_levels.items():
            annotation_xpath = Tsadra_template.toc_xpaths.get(annotation_name, "")
            if annotation_xpath and annotation_name in serialized_html:
                new_toc_levels[walker] = annotation_xpath
                walker += 1
        return new_toc_levels
    
    def get_new_metadata(self, soup, meta_data):
        """Update meta data of opf

        Args:
            soup (bs4-tag): beautiful soup tag of whole opf
            meta_data (bs4-tag): beautiful soup tag of metadata

        Returns:
            bs4-tag: new metadata
        """
        ibook_meta = soup.new_tag('meta')
        ibook_meta.attrs['property'] = "ibooks:specified-fonts"
        ibook_meta.append('true')
        meta_data.append(ibook_meta)
        return meta_data

    def get_new_manifest(self, soup, manifest):
        """Update manifest of opf

        Args:
            soup (bs4-tag): beautiful soup tag of whole opf
            manifest (bs4-tag): beautiful soup tag of manifest

        Returns:
            bs4-tag: new manifest
        """
        new_item = soup.new_tag('item')
        new_item.attrs['href'] = "font/MonlamUniOuChan2.ttf"
        new_item.attrs['id'] = "MonlamUniOuChan2.ttf"
        new_item.attrs['media-type'] = "application/x-font-ttf"
        manifest.append(new_item)
        return manifest

    def get_new_opf(self, opf):
        """Updating opf content of epub with ibook specifications

        Args:
            opf (str): opf content of epub produced by calibre

        Returns:
            str: new opf content
        """
        soup = BeautifulSoup(opf, "html.parser")
        soup.package.attrs['prefix'] = "ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
        old_meta = soup.find('metadata')
        old_manifest = soup.find('manifest')
        new_meta = self.get_new_metadata(soup, old_meta)
        new_manifest = self.get_new_manifest(soup, old_manifest)
        soup.metadata.replaceWith(new_meta)
        soup.manifest.replaceWith(new_manifest)
        return str(soup)

    def embed_ibook_specific_font(self, epub_path):
        """Include ibook specification for proper font embedding and recompiling the ebook.

        Args:
            epub_path (path_obj): path of epub produced by calibre
        """
        pecha_id = epub_path.stem
        #rename to zip
        zip_path = epub_path.parent / f'{pecha_id}.zip'
        os.rename(str(epub_path), str(zip_path))
        # epub_path.rename(epub_path.with_suffix('.zip'))
        epub_folder = str(epub_path.parent / f'{pecha_id}')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(epub_folder)
        print('INFO: Unzip epub..')
        zip_path.unlink()
        opf_path = Path(epub_folder) / 'content.opf'
        opf_content = opf_path.read_text(encoding='utf-8')
        new_opf_content = self.get_new_opf(opf_content)
        opf_path.write_text(new_opf_content, encoding='utf-8')
        print('INFO: OPF content updated..')
        new_zip_path = shutil.make_archive(epub_folder, 'zip', epub_folder)
        os.system(f'rm -r {epub_folder}')
        print('INFO: file zipped..')
        new_zip_path = Path(new_zip_path)
        new_epub_path = f'{epub_folder}.epub'
        os.rename(str(new_zip_path), new_epub_path)
        # new_zip_path.rename(new_zip_path.with_suffix('.epub'))
        print('INFO: Epub ready...')

    def get_serialized_html(self, result, vol_id, pecha_title):
        result = f"{self.get_front_page()}{result}"
        footnote_ref_tag = ""
        if "Footnote" in self.layers:
            footnote_fn = self.opf_path / "layers" / vol_id / "Footnote.yml"
            footnote_layer = load_yaml(footnote_fn)
            footnote_ref_tag = self.get_footnote_references(
                footnote_layer["annotations"]
            )
        result = self.p_tag_adder(result)
        result = self.indentation_adjustment(result)
        serialized_html = (
            f"<html>\n<head>\n\t<title>{pecha_title}</title>\n</head>\n<body>\n"
        )
        serialized_html += f"{result}{footnote_ref_tag}</body>\n</html>"
        return serialized_html

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
            serialized_html = self.get_serialized_html(result, vol_id, pecha_title)
            Path(out_html_fn).write_text(serialized_html)
            # Downloading css template file from ebook template repo and saving it
            template = requests.get(
                "https://raw.githubusercontent.com/OpenPecha/ebook-template/master/tsadra_template.css"
            )
            Path("template.css").write_bytes(template.content)
            # Running ebook-convert command to convert html file to .epub (From calibre)
            # XPath expression to detect chapter titles.
            if not toc_levels:
                toc_levels = Tsadra_template.toc_levels
            toc_levels = self.set_toc_level(toc_levels, serialized_html)
            level1_toc_Xpath = toc_levels.get(1, "")
            level2_toc_Xpath = toc_levels.get(2, "")
            level3_toc_Xpath = toc_levels.get(3, "")

            cover_path = self.opf_path / f"assets/image/{cover_image}"
            out_epub_fn = output_path / f"{self.meta['id']}.epub"
            font_family = "Monlam Uni Ouchan2"
            if cover_path.is_file():
                os.system(
                    f'ebook-convert {out_html_fn} {out_epub_fn} --extra-css=./template.css --embed-font-family="{font_family}" --page-breaks-before="{Tsadra_template.book_title_Xpath}" --cover={cover_path} --flow-size=0 --level1-toc="{level1_toc_Xpath}" --level2-toc="{level2_toc_Xpath}" --level3-toc="{level3_toc_Xpath}" --use-auto-toc --disable-font-rescaling'
                )
            else:
                os.system(
                    f'ebook-convert {out_html_fn} {out_epub_fn} --extra-css=./template.css --embed-font-family="{font_family}" --page-breaks-before="{Tsadra_template.book_title_Xpath}" --flow-size=0 --level1-toc="{level1_toc_Xpath}" --level2-toc="{level2_toc_Xpath}" --level3-toc="{level3_toc_Xpath}" --use-auto-toc --disable-font-rescaling'
                )
            # Removing html file and template file
            os.system(f"rm {out_html_fn}")
            os.system("rm template.css")
            if out_epub_fn.is_file():
                self.embed_ibook_specific_font(out_epub_fn)
            return out_epub_fn
