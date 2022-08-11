import gzip
import json
import math
import re
from enum import Enum
from pathlib import Path

import datetime
from datetime import timezone
import requests
from antx import transfer
from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD

from openpecha.core.annotation import Page, Span
from openpecha.core.annotations import BaseAnnotation
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.ids import get_base_id
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType, LicenseType, CopyrightStatus, Copyright
from openpecha.formatters import BaseFormatter
from openpecha.utils import dump_yaml, gzip_str


BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")

extended_LayerEnum = [(l.name, l.value) for l in LayerEnum] + [("low_conf_box", "LowConfBox")] + [("language", "Language")]
LayerEnum = Enum("LayerEnum", extended_LayerEnum)

class ExtentedLayer(Layer):
    annotation_type: LayerEnum

class LowConfBox(BaseAnnotation):
    confidence: str

class Language(BaseAnnotation):
    language_code: str

class GoogleOCRFormatter(BaseFormatter):
    """
    OpenPecha Formatter for Google OCR JSON output of scanned pecha.
    """

    def __init__(self, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
        self.n_page_breaker_char = 3
        self.page_break = "\n" * self.n_page_breaker_char
        self.base_text = []
        self.low_conf_ann_text = ""
        self.base_meta = {}
        self.cur_base_word_confidences = []
        self.word_confidences = []

    def text_preprocess(self, text):

        return text

    def get_bounding_poly_mid(self, bounding_poly):
        """Calculate middle of the bounding poly vertically using y coordinates of the bounding poly

        Args:
            bounding_poly (dict): bounding poly's details

        Returns:
            float: mid point's y coordinate of bounding poly
        """
        y1 = bounding_poly["boundingBox"]["vertices"][0].get("y", 0)
        y2 = bounding_poly["boundingBox"]["vertices"][2].get("y", 0)
        y_avg = (y1 + y2) / 2
        return y_avg

    def get_avg_bounding_poly_height(self, bounding_polys):
        """Calculate the average height of bounding polys in page

        Args:
            bounding_polys (list): list of boundingpolys

        Returns:
            float: average height of bounding ploys
        """
        height_sum = 0
        for bounding_poly in bounding_polys:
            y1 = bounding_poly["boundingBox"]["vertices"][0].get("y", 0)
            y2 = bounding_poly["boundingBox"]["vertices"][2].get("y", 0)
            height_sum += y2 - y1
        avg_height = height_sum / len(bounding_polys)
        return avg_height

    def is_in_cur_line(self, prev_bounding_poly, bounding_poly, avg_height):
        """Check if bounding poly is in same line as previous bounding poly
        a threshold to check the conditions set to 10 but it can varies for pecha to pecha

        Args:
            prev_bounding_poly (dict): previous bounding poly
            bounding_poly (dict): current bounding poly
            avg_height (float): average height of all the bounding polys in page

        Returns:
            boolean: true if bouding poly is in same line as previous bounding poly else false
        """
        threshold = 10
        if (
            self.get_bounding_poly_mid(bounding_poly)
            - self.get_bounding_poly_mid(prev_bounding_poly)
            < avg_height / threshold
        ):
            return True
        else:
            return False

    def get_low_confidence_ann(self, bounding_poly):
        if bounding_poly['confidence'] >0.9:
            return bounding_poly.get("text", "")
        else:
            return f"§{bounding_poly.get('text', '')}Ç{bounding_poly['confidence']}Ç§"
    
    def get_language_code(self, bounding_poly):
        language_codes = []
        properties = bounding_poly.get("property", {})
        if properties:
            languages = properties.get("detectedLanguages", [])
            if languages:
                for language in languages:
                    if language_code := language.get("languageCode", ""):
                        language_codes.append(language_code)
        return language_codes
    
    def get_language_code_ann(self, bounding_poly):
        text = bounding_poly.get("text", "")
        language_codes = self.get_language_code(bounding_poly)
        if language_codes:
            language_code = "-".join(language_codes)
            return f"§{text}Ç{language_code}Ç§"
        else:
            return text

    def get_lines(self, bounding_polys):
        """Return list of lines in page using bounding polys of page

        Args:
            bounding_polys (list): list of all the bounding polys

        Returns:
            list: list of lines in page
        """
        lines = {
            'base_lines': [],
            'low_conf_annotated_lines': [],
            'language_code_annotated_lines': []
        }
        prev_bounding_poly = bounding_polys[0]
        base_lines = []
        low_conf_annotated_lines = []
        language_code_annotated_lines = []
        cur_base_line = ''
        cur_low_conf_annotated_line = ''
        cur_language_code_annotated_line = ''
        avg_line_height = self.get_avg_bounding_poly_height(bounding_polys)
        for bounding_poly in bounding_polys:
            if self.is_in_cur_line(prev_bounding_poly, bounding_poly, avg_line_height):
                cur_base_line += bounding_poly.get("text", "")
                cur_low_conf_annotated_line += self.get_low_confidence_ann(bounding_poly)
                cur_language_code_annotated_line += self.get_language_code_ann(bounding_poly)
            else:
                base_lines.append(cur_base_line)
                low_conf_annotated_lines.append(cur_low_conf_annotated_line)
                language_code_annotated_lines.append(cur_language_code_annotated_line)
                cur_base_line = bounding_poly.get("text", "")
                cur_low_conf_annotated_line = self.get_low_confidence_ann(bounding_poly)
                cur_language_code_annotated_line = self.get_language_code_ann(bounding_poly)
            prev_bounding_poly = bounding_poly
        if cur_base_line:
            base_lines.append(cur_base_line)
        if cur_low_conf_annotated_line:
            low_conf_annotated_lines.append(cur_low_conf_annotated_line)
        if cur_language_code_annotated_line:
            language_code_annotated_lines.append(cur_language_code_annotated_line)
        lines["base_lines"] = base_lines
        lines["low_conf_annotated_lines"] = low_conf_annotated_lines
        lines['language_code_annotated_lines'] = language_code_annotated_lines
        return lines

    def transfer_space(self, base_with_space, base_without_space):
        """transfer space from base with space to without space

        Args:
            base_with_space (str): base with space which is extracted from page['textAnnotations'][0]['description']
            base_without_space (str): base without space as it is generated using accumulating non space char only

        Returns:
            [str]: page content
        """
        new_base = transfer(
            base_with_space, [["space", r"( )"]], base_without_space, output="txt"
        )
        return new_base

    def find_centriod(self, bounding_poly):
        """Calculate centriod of bounding poly

        Args:
            bounding_poly (dict): info regarding bounding poly such as vertices and description

        Returns:
            list: centriod coordinates
        """
        sum_of_x = 0
        sum_of_y = 0
        for vertice in bounding_poly["boundingBox"]["vertices"]:
            sum_of_x += vertice['x']
            sum_of_y += vertice['y']
        centriod = [sum_of_x/4, sum_of_y/4]
        return centriod

    def get_poly_sorted_on_y(self, bounding_poly_centriods):
        """Sort bounding polys centriod base on y coordinates

        Args:
            bounding_poly_centriods (list): list of centriod coordinates

        Returns:
            list: list centriod coordinated sorted base on y coordinate
        """
        sorted_on_y_polys = sorted(bounding_poly_centriods , key=lambda k: [k[1]])
        return sorted_on_y_polys

    def get_poly_sorted_on_x(self, sorted_on_y_polys, avg_box_height):
        """Groups box belonging in same line using average height and sort the grouped boxes base on x coordinates

        Args:
            sorted_on_y_polys (list): list of centriod
            avg_box_height (float): average boxes height

        Returns:
            list: list of sorted centriod
        """
        prev_bounding_poly = sorted_on_y_polys[0]
        lines = []
        cur_line = []
        sorted_polys = []
        for bounding_poly in sorted_on_y_polys:
            if abs(bounding_poly[1]-prev_bounding_poly[1]) < avg_box_height/10:
                cur_line.append(bounding_poly)
            else:
                lines.append(cur_line)
                cur_line = []
                cur_line.append(bounding_poly)
            prev_bounding_poly = bounding_poly
        if cur_line:
            lines.append(cur_line)
        for line in lines:
            sorted_line = sorted(line, key=lambda k: [k[0]])
            for poly in sorted_line:
                sorted_polys.append(poly)
        return sorted_polys

    def sort_bounding_polys(self, main_region_bounding_polys):
        """Sort the bounding polys

        Args:
            main_region_bounding_polys (list): list of bounding polys

        Returns:
            list: sorted bounding poly list
        """
        bounding_polys = {}
        bounding_poly_centriods = []
        avg_box_height = self.get_avg_bounding_poly_height(main_region_bounding_polys)
        for bounding_poly in main_region_bounding_polys:
            centroid = self.find_centriod(bounding_poly)
            bounding_polys[f"{centroid[0]},{centroid[1]}"] = bounding_poly
            bounding_poly_centriods.append(centroid)
        sorted_bounding_polys = []
        sort_on_y_polys = self.get_poly_sorted_on_y(bounding_poly_centriods)
        sorted_bounding_poly_centriods = self.get_poly_sorted_on_x(sort_on_y_polys, avg_box_height)
        for bounding_poly_centriod in sorted_bounding_poly_centriods:
            sorted_bounding_polys.append(bounding_polys[f"{bounding_poly_centriod[0]},{bounding_poly_centriod[1]}"])
        return sorted_bounding_polys

    def get_char_base_bounding_polys(self, response):
        bounding_polys = []
        cur_word = ""
        for page in response['fullTextAnnotation']['pages']:
            for block in page['blocks']:
                for paragraph in block['paragraphs']:
                    for word in paragraph['words']:
                        for symbol in word['symbols']:
                            cur_word += symbol['text']
                        word['text'] = cur_word
                        cur_word = ""
                        bounding_polys.append(word)
        return bounding_polys

    def populate_confidence(self, bounding_polys):
        for bounding_poly in bounding_polys:
            self.word_confidences.append(float(bounding_poly['confidence']))
            self.cur_base_word_confidences.append(float(bounding_poly['confidence']))

    def post_process_page(self, page):
        """parse page response to generate page content by reordering the bounding polys

        Args:
            page (dict): page content response given by google ocr engine

        Returns:
            str: page content
        """
        post_processed_pages = {
            'base_page': '',
            'low_conf_annotated_page': '',
            'language_code_annotated_page': ''
        }
        postprocessed_page_content = ""
        try:
            page_content = page["textAnnotations"][0]["description"]
        except Exception:
            print("Page empty!!")
            return postprocessed_page_content
        bounding_polys = self.get_char_base_bounding_polys(page)
        self.populate_confidence(bounding_polys)
        sorted_bounding_polys = self.sort_bounding_polys(bounding_polys)
        lines = self.get_lines(sorted_bounding_polys)
        page_content_without_space = "\n".join(lines.get("base_lines", []))
        page_with_low_conf_ann = "\n".join(lines.get("low_conf_annotated_lines", []))
        page_with_language_code_ann = "\n".join(lines.get("language_code_annotated_lines", []))
        postprocessed_page_content = self.transfer_space(
            page_content, page_content_without_space
        )
        postprocessed_pg_with_low_conf_ann = self.transfer_space(postprocessed_page_content, page_with_low_conf_ann)
        postprocessed_pg_with_language_code_ann = self.transfer_space(postprocessed_page_content, page_with_language_code_ann)
        post_processed_pages["base_page"] = postprocessed_page_content + "\n"
        post_processed_pages["low_conf_annotated_page"] = postprocessed_pg_with_low_conf_ann + "\n"
        post_processed_pages["language_code_annotated_page"] = postprocessed_pg_with_language_code_ann + "\n"
        return post_processed_pages


    def get_input(self, input_path):
        """
        load and return all jsons in the input_path.
        """
        for fn in sorted(list(input_path.iterdir())):
            if fn.name.split(".")[0] == "info":
                continue
            try:
                if fn.suffix == ".gz":
                    yield json.load(gzip.open(str(fn), "rb")), fn.stem.split(".")[0]
                else:
                    yield json.load(fn.open()), fn.stem
            except GeneratorExit:
                return None, None
            except Exception:
                yield None, None

    def extract_confidence(self, chunk):
        confidence = re.search("Ç(.+?)Ç", chunk).group(1)
        return confidence
        
    def format_low_confidence_box_layer(self, low_conf_ann_text):
        base_text = ""
        anns = {}
        low_conf_ann_text = low_conf_ann_text.replace("\n", "¢")
        chunks = re.split("(§.+?§)", low_conf_ann_text)
        for chunk in chunks:
            if re.search("§.+?§", chunk):
                start = len(base_text)
                confidence = self.extract_confidence(chunk)
                base_text += re.search("§(.+?)Ç", chunk).group(1)
                end = len(base_text)
                span = Span(start=start, end=end)
                uuid = self.get_unique_id()
                low_conf_ann = LowConfBox(span=span, confidence=confidence)
                anns[uuid] = low_conf_ann
            else:
                base_text += chunk
        layer = ExtentedLayer(annotation_type=LayerEnum.low_conf_box, annotations=anns)
        return json.loads(layer.json(exclude_none=True))
    
    def extract_language_code(self, chunk):
        language_code = re.search("Ç(.+?)Ç", chunk).group(1)
        return language_code
    
    def extract_text(self, chunk):
        text = re.search('§(.+?)Ç.+?Ç', chunk).group(1)
        return text

    def process_first_chunk(self, chunk):
        try:
            cur_annotated_chunk = self.extract_text(chunk)
        except:
            cur_annotated_chunk = ""
        try:
            cur_language_code = self.extract_language_code(chunk)
        except:
            cur_language_code = ""
        return cur_annotated_chunk, cur_language_code

    def rm_short_ann(self, text):
        new_text = text
        for ann in re.findall("(§.+?§)", text):
            ann_text = self.extract_text(ann)
            ann  = re.escape(ann)
            if len(ann_text) < 30:
                new_text = re.sub(ann, ann_text, new_text, 1)
        return new_text

    def add_default_lang_code(self, text):
        new_text = ""
        chunks = re.split("(§.+?§)", text)
        for chunk in chunks:
            if chunk:
                if re.search("(§.+?§)", chunk):
                    new_text += chunk
                else:
                    new_text += f"§{chunk}ÇboÇ§"
        return new_text

    def is_mergeable_chunk(self, prev_chunk, chunk, last_lang_code):
        if re.search("§.+?§", prev_chunk) or prev_chunk == "¢":
            try:
                prev_lang_code = self.extract_language_code(prev_chunk)
            except:
                prev_lang_code =last_lang_code
            cur_lang_code = self.extract_language_code(chunk)
            if prev_lang_code == cur_lang_code:
                return True
        return False

    def merge_consecutive_ann(self, ann_text):
        new_text = ""
        chunks = re.split("(§.+?§)", ann_text)
        if chunks:
            cur_annotated_chunk, cur_language_code = self.process_first_chunk(chunks[0])
            if not cur_annotated_chunk:
                new_text += chunks[0]
            prev_chunk = chunks[0]
            for chunk in chunks[1:]:
                if chunk:
                    if re.search("§.+?§", chunk):
                        if self.is_mergeable_chunk(prev_chunk, chunk, cur_language_code):
                            if cur_annotated_chunk:
                                cur_annotated_chunk += self.extract_text(chunk)
                            else:
                                cur_annotated_chunk += f"§{self.extract_text(chunk)}"
                            cur_language_code = self.extract_language_code(chunk)
                        else:
                            if cur_annotated_chunk:
                                new_text += f"{cur_annotated_chunk}Ç{cur_language_code}Ç§"
                                cur_annotated_chunk = f"§{self.extract_text(chunk)}"
                                cur_language_code = self.extract_language_code(chunk)
                            else:
                                cur_annotated_chunk = f"§{self.extract_text(chunk)}"
                                cur_language_code = self.extract_language_code(chunk)
                    elif chunk == "¢":
                        if cur_annotated_chunk:
                            cur_annotated_chunk += chunk
                        else:
                            new_text += chunk
                    else:
                        if cur_annotated_chunk:
                            new_text += f"{cur_annotated_chunk}Ç{cur_language_code}Ç§"
                            cur_annotated_chunk = ""
                            cur_language_code = ""
                        new_text += chunk
                    prev_chunk = chunk
            if cur_annotated_chunk:
                new_text += f"{cur_annotated_chunk}Ç{cur_language_code}Ç§"
            new_text = self.rm_short_ann(new_text)
            new_text = self.add_default_lang_code(new_text)
            new_text = re.sub("(¢)(Ç.+?Ç§)", "\g<2>\g<1>", new_text)
        else:
            new_text = ann_text
        return new_text

    def format_language_layer(self, language_code_annotated_text):
        base_text = ""
        anns = {}
        language_code_annotated_text = language_code_annotated_text.replace("\n", "¢")
        language_code_annotated_text = self.merge_consecutive_ann(language_code_annotated_text)
        chunks = re.split("(§.+?§)", language_code_annotated_text)
        for chunk in chunks:
            if re.search("§.+?§", chunk):
                start = len(base_text)
                lanuage_code = self.extract_language_code(chunk)
                base_text += re.search("§(.+?)Ç", chunk).group(1)
                end = len(base_text)
                span = Span(start=start, end=end)
                uuid = self.get_unique_id()
                language_ann = Language(span=span, language_code=lanuage_code)
                anns[uuid] = language_ann
            else:
                base_text += chunk
        layer = ExtentedLayer(annotation_type=LayerEnum.language, annotations=anns)
        return json.loads(layer.json(exclude_none=True))


    def format_layer(self, layers, base_id):
        anns = {}
        for (start, end, n_pg), page_ref in zip(layers["base_pages"], layers["pages_ref"]):
            uuid = self.get_unique_id()
            span = Span(start=start, end=end)
            page = Page(span=span, imgnum=n_pg, reference=page_ref)
            anns[uuid] = page

        layer = ExtentedLayer(annotation_type=LayerEnum.pagination, annotations=anns)
        result = {
            LayerEnum.pagination.value: json.loads(layer.json(exclude_none=True))
        }
        result[LayerEnum.low_conf_box.value] = self.format_low_confidence_box_layer(layers['low_conf_ann_text'])
        result[LayerEnum.language.value] = self.format_language_layer(layers['language_code_annotated_text'])

        return result

    def _get_coord(self, vertices):
        coord = []
        for vertice in vertices:
            coord.append((vertice["x"], vertice["y"]))

        return coord

    def _get_page(self, response):
        pages = {
            'base_page': '',
            'low_conf_annotated_page': '',
            'language_code_annotated_page': ''
        }
        try:
            if len(response["textAnnotations"]) != 0:
                page = response["textAnnotations"][0]
            else:
                return pages
        except KeyError:
            return pages

        pages = self.post_process_page(response)
        # vertices = page['boundingPoly']['vertices']  # get text box

        return pages # self._get_coord(vertices)

    def _get_lines(self, text, last_pg_end_idx, is_first_pg):
        lines = []
        line_breaks = [m.start() for m in re.finditer("\n", text)]

        start = last_pg_end_idx

        # increase the start idx with page_breaker_char for page greater than frist page.
        if not is_first_pg:
            start += self.n_page_breaker_char + 1
            line_breaks = list(map(lambda x: x + start, line_breaks))

        for line in line_breaks:
            lines.append((start, line - 1))  # skip new_line, which has 1 char length
            start += (line - start) + 1

        return lines, line

    def save_boundingPoly(self, response, path):
        def tlbr(vertices):
            return {"tl": vertices[0], "br": vertices[2]}

        boundingPolies = {}
        for ann in response["textAnnotations"]:
            boundingPolies[ann["description"]] = tlbr(ann["boundingPoly"]["vertices"])

        zipped_boundingPolies = gzip_str(json.dumps(boundingPolies))
        path.write_bytes(zipped_boundingPolies)

    def save_low_conf_char(self, response, path):
        char_idx = 0
        low_conf_chars = ""
        for page in response["fullTextAnnotation"]["pages"]:
            for block in page["blocks"]:
                for paragraph in block["paragraphs"]:
                    for word in paragraph["words"]:
                        for symbol in word["symbols"]:
                            if symbol.get("confidence", 1) < 0.9:
                                low_conf_chars += f'{symbol["text"]} {char_idx}\n'
                            char_idx += 1
        if low_conf_chars:
            path.write_bytes(gzip_str(low_conf_chars))

    @staticmethod
    def _get_imagelist_meta(vol_name):
        r = requests.get(f"http://iiifpres.bdrc.io/il/v:bdr:{vol_name}")
        img2seq = {}
        for i, img in enumerate(r.json(), start=1):
            name, ext = img["filename"].split(".")
            img2seq[name] = {"num": i, "ext": ext}
        return img2seq

    def build_layers(self, responses, vol_name, base_id=None):

        base_pages = []
        low_conf_ann_pages = []
        language_code_ann_pages = []
        pages_ref = []
        last_pg_end_idx = 0
        img2seq = self._get_imagelist_meta(vol_name)
        for response, page_ref in responses:
            n_pg = img2seq[page_ref]["num"]

            # extract annotation
            if not response:
                print(f"[ERROR] Failed : {n_pg}")
                continue
            pages = self._get_page(response)
            base_page = pages['base_page']
            low_conf_ann_page = pages['low_conf_annotated_page']
            language_code_ann_page = pages['language_code_annotated_page']

            # skip empty page (can be bad image)
            if not base_page:
                print(f"[ERROR] empty page {n_pg}")
                continue
            lines, last_pg_end_idx = self._get_lines(base_page, last_pg_end_idx, n_pg == 1)
            base_pages.append((lines[0][0], lines[-1][1], n_pg))
            pages_ref.append(f"{page_ref}.{img2seq[page_ref]['ext']}")

            # create base_text
            self.base_text.append(base_page)
            low_conf_ann_pages.append(low_conf_ann_page)
            language_code_ann_pages.append(language_code_ann_page)
        low_conf_ann_text = f"{self.page_break}".join(low_conf_ann_pages)
        language_code_annotated_text = f"{self.page_break}".join(language_code_ann_pages)

        result = {
            "base_pages": base_pages,
            "pages_ref": pages_ref,
            "low_conf_ann_text": low_conf_ann_text,
            "language_code_annotated_text": language_code_annotated_text
            }

        return result

    def get_base_text(self):
        base_text = f"{self.page_break}".join(self.base_text)
        self.base_text = []

        return base_text

    def get_resource_ttl(self, work_id):
        try:
            ttl = requests.get(f"https://ldspdi.bdrc.io/resource/M{work_id}.ttl")
            return ttl.text
        except:
            return None

    def get_copyright_and_license_info(self, work_id):
        ttl = self.get_resource_ttl(work_id)
        if ttl:
            g = Graph()
            try:
                g.parse(data=ttl, format="ttl")
            except:
                return {}, None
            
            work = f"M{work_id}"
            status = g.value(BDR[work], BDO['copyrightStatus'])
            copyright_status = (str(status)).split("/")[-1]
            
            copyright_copyrighted = Copyright(
                status=CopyrightStatus.COPYRIGHTED,
                notice="Copyrighted by the original author or editor",
                info_url="https://rightsstatements.org/page/InC/1.0/?language=en",
            )
            
            copyright_unknown = Copyright(
                status=CopyrightStatus.UNKNOWN,
                notice="Copyright Undertermined",
                info_url="https://rightsstatements.org/page/UND/1.0/?language=en",
            )
            
            copyright_public_domain = Copyright(
                status=CopyrightStatus.PUBLIC_DOMAIN,
                notice="Public Domain",
                info_url="https://wiki.creativecommons.org/wiki/Public_domain",
            )
            
            if copyright_status == "CopyrightUndetermined":
                license = LicenseType.UNDER_COPYRIGHT
                return copyright_unknown, license
            elif copyright_status == "None":
                license = LicenseType.CC0
                return copyright_public_domain, license
            elif copyright_status == "Copyrighted":
                license = LicenseType.UNDER_COPYRIGHT
                return copyright_copyrighted, license
        else:
            return {}, None
        
    

    def get_admindata_ttl(self, work_id):
        try:
            ttl = requests.get(f"http://purl.bdrc.io/admindata/{work_id}.ttl")
            return ttl.text
        except:
            return None

    def get_restrictedInChina_and_access_info(self, work_id):
        ttl = self.get_admindata_ttl(work_id)
        if ttl:
            g = Graph()
            try:
                g.parse(data=ttl, format="ttl")
            except:
                return None, None
            
            restrictedInChina = (g.value(BDA[work_id], ADM['restrictedInChina'])).value
            
            output = g.value(BDA[work_id], ADM['access'])
            access = (str(output)).split("/")[-1]
            
            return restrictedInChina, f"http://purl.bdrc.io/admindata/{access}"
        else:
            return None, None
            
    def get_metadata(self, work_id, pecha_id):
        import xml.etree.ElementTree as ET

        import requests
        from pyewts import pyewts

        converter = pyewts()
        query_url = "https://www.tbrc.org/xmldoc?rid={}"
        bdrc_metadata_url = query_url.format(work_id)
        r = requests.get(bdrc_metadata_url)

        opf_word_confidence_median = self.get_median(self.word_confidences)
        opf_word_confidence_mean = self.get_mean(self.word_confidences)
        
        restrictedInChina, access = self.get_restrictedInChina_and_access_info(work_id)
        copyright, license = self.get_copyright_and_license_info(work_id)
            

        try:
            root = ET.fromstring(r.content.decode("utf-8"))
        except Exception:
            metadata = InitialPechaMetadata(
                source='https://library.bdrc.io',
                initial_creation_type=InitialCreationType.ocr,
                imported=datetime.datetime.now(timezone.utc),
                last_modified=datetime.datetime.now(timezone.utc),
                parser=None,
                copyright=copyright,
                license=license,
                ocr_word_mean_confidence_index=opf_word_confidence_mean,
                ocr_word_median_confidence_index=opf_word_confidence_median,
                source_metadata={
                    "id": f"bdrc:{work_id}",
                    "title": "",
                    "author": "",
                    "restrictedInChina": restrictedInChina,
                    "access": access
                },
                base=self.base_meta
            )
            return json.loads(metadata.json())

        title_tag = root[0]
        author_tag = root.find("{http://www.tbrc.org/models/work#}creator")
        metadata = InitialPechaMetadata(
                source='https://library.bdrc.io',
                initial_creation_type=InitialCreationType.ocr,
                imported=datetime.datetime.now(timezone.utc),
                last_modified=datetime.datetime.now(timezone.utc),
                parser=None,
                copyright=copyright,
                license=license,
                ocr_word_mean_confidence_index=opf_word_confidence_mean,
                ocr_word_median_confidence_index=opf_word_confidence_median,
                source_metadata={
                    "id": f"bdrc:{work_id}",
                    "title": converter.toUnicode(title_tag.text),
                    "author": converter.toUnicode(author_tag.text) if author_tag else "",
                    "restrictedInChina": restrictedInChina,
                    "access": access
                },
                base=self.base_meta
        )

        return json.loads(metadata.json())
    
    def get_median(self, list_):
        list_.sort()
        number_of_items = len(list_)
        mid_index = number_of_items // 2
        if number_of_items % 2 == 0:
            return (list_[mid_index-1] + list_[mid_index]) / 2
        else:
            return list_[mid_index]
    
    def get_mean(self, list_):
        grand_sum = sum(list_)
        mean_ = grand_sum / len(list_)
        return mean_


    def get_base_confidence_median(self):
        cur_base_confidences = self.cur_base_word_confidences
        base_confidence_median = self.get_median(cur_base_confidences)
        return base_confidence_median
    
    def get_base_confidence_mean(self):
        cur_base_confidences = self.cur_base_word_confidences
        base_confidence_mean = self.get_mean(cur_base_confidences)
        return base_confidence_mean

    def set_base_meta(self, meta_ttl, image_group_id, base_file_name):
        BDR = Namespace("http://purl.bdrc.io/resource/")
        BDO = Namespace("http://purl.bdrc.io/ontology/core/")
        g = Graph()
        try:
            g.parse(data=meta_ttl, format="ttl")
        except:
            return {}
        volume_number = int(g.value(BDR[image_group_id], BDO["volumeNumber"]))
        title = g.value(BDR[image_group_id], RDFS.comment)
        if title:
            title = title.value
        else:
            title = ""
        
        try:
            total_pages = int(g.value(BDR[image_group_id], BDO["volumePagesTotal"]))
        except:
            total_pages = 0
        base_confidence_median = self.get_base_confidence_median()
        base_confidence_mean = self.get_base_confidence_mean()
        self.cur_word_confidences = []
        self.base_meta[base_file_name] = {
            "source_metadata": {
                "image_group_id": image_group_id,
                "title": title,
                "total_pages": total_pages,
            },
            "order": volume_number,
            "base_file": f"{base_file_name}.txt",
            "ocr_word_median_confidence_index": base_confidence_median,
            "ocr_word_mean_confidence_index": base_confidence_mean
        }

    def get_meta_ttl(self, work_id):
        """Download ttl file of work and save in meta_ttl.
        Args:
            work_id (str): work id
        """
        try:
            ttl = requests.get(f"http://purl.bdrc.io/graph/{work_id}.ttl")
            return ttl.text
        except:
            print(' TTL not Found!!!')
            return ""
    
    def create_opf(self, input_path, pecha_id, meta_flag=True):
        """Create opf of google ocred pecha

        Args:
            input_path (str): input path
            pecha_id (str): pecha id
            meta_flag (bool, optional): True if meta data needed else false. Defaults to True.

        Returns:
            path: opf path
        """
        input_path = Path(input_path)
        self._build_dirs(input_path, id_=pecha_id)


        for i, vol_path in enumerate(sorted(input_path.iterdir())):
            print(f"[INFO] Processing {input_path.name}-{vol_path.name} ...")
            base_id = get_base_id()
            if (self.dirs["opf_path"] / "base" / f"{base_id}.txt").is_file():
                continue
            responses = self.get_input(vol_path)
            layers = self.build_layers(responses, vol_path.name, base_id)
            formatted_layers = self.format_layer(layers, base_id)
            base_text = self.get_base_text()

            # save base_text
            (self.dirs["opf_path"] / "base" / f"{base_id}.txt").write_text(base_text)

            # save layers
            vol_layer_path = self.dirs["layers_path"] / base_id
            vol_layer_path.mkdir(exist_ok=True)
            for layer, ann in formatted_layers.items():
                layer_fn = vol_layer_path / f"{layer}.yml"
                dump_yaml(ann, layer_fn)
            
            #create base of source_metadata    
            meta_ttl = self.get_meta_ttl(input_path.name)
            self.set_base_meta(meta_ttl, vol_path.name, base_id)

        # create meta.yml
        if meta_flag:
            meta_fn = self.dirs["opf_path"] / "meta.yml"
            dump_yaml(self.get_metadata(input_path.name, pecha_id), meta_fn)

        return self.dirs["opf_path"].parent


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf("../../Esukhia/img2opf/archive/output/W1PD95844", 300)
