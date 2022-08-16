import gzip
import json
import math
import re
from enum import Enum
from pathlib import Path
import statistics
import logging

import datetime
from datetime import timezone
import requests
from pathlib import Path

from openpecha.core.annotation import Page, Span
from openpecha.core.annotations import BaseAnnotation, Language
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.ids import get_base_id
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType, LicenseType, CopyrightStatus, Copyright, Copyright_copyrighted, Copyright_unknown, Copyright_public_domain
from openpecha.formatters import BaseFormatter
from openpecha.utils import dump_yaml, gzip_str

from openpecha.buda.api import get_buda_scan_info, get_image_list

extended_LayerEnum = [(l.name, l.value) for l in LayerEnum] + [("low_conf_box", "LowConfBox")]
LayerEnum = Enum("LayerEnum", extended_LayerEnum)

class ExtentedLayer(Layer):
    annotation_type: LayerEnum

class LowConfBox(BaseAnnotation):
    confidence: str

class BBox:
    def __init__(self, text: str, vertices: list, confidence: float, language: str):

        self.text = text
        self.vertices = vertices
        self.confidence = confidence
        self.language = language
    

    
    def get_box_height(self):
        y1 = self.vertices[0][1]
        y2 = self.vertices[1][1]
        height = abs(y2-y1)
        return height
    
    
    def get_box_orientation(self):
        x1= self.vertices[0][0]
        x2 = self.vertices[1][0]
        y1= self.vertices[0][1]
        y2 = self.vertices[1][1]
        width = abs(x2-x1)
        length = abs(y2-y1)
        if width > length:
            return "landscape"
        else:
            return "portrait"

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
        self.bdrc_scan_id = None
        self.metadata = {}
        self.default_language = None
        self.buda_data = {}

    def text_preprocess(self, text):

        return text

    def get_bounding_poly_mid(self, bounding_poly):
        """Calculate middle of the bounding poly vertically using y coordinates of the bounding poly

        Args:
            bounding_poly (dict): bounding poly's details

        Returns:
            float: mid point's y coordinate of bounding poly
        """
        y1 = bounding_poly.vertices[0][1]
        y2 = bounding_poly.vertices[2][1]
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
            y1 = bounding_poly.vertices[0][1]
            y2 = bounding_poly.vertices[2][1]
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

    def get_low_confidence_ann(self, bounding_poly, char_walker):
        """Annotate poly having confidence index less than 0.9 or 90%

        Args:
            bounding_poly (bbox): bbox object

        Returns:
            text: text annotated with low confidence annotation
        """
        ann = {}
        if bounding_poly.confidence >0.9:
            return None, char_walker + len(bounding_poly.text)
        else:
            end = char_walker + len(bounding_poly.text)
            span = Span(start=char_walker, end=end)
            uuid = self.get_unique_id()
            low_conf_ann = LowConfBox(span=span, confidence=bounding_poly.confidence)
            ann[uuid] = low_conf_ann
            return ann, end
    
    def get_language_code(self, bounding_poly):
        """Returns language code of the bounding poly

        Args:
            bounding_poly (dict): bounding poly info

        Returns:
            str: language code of the bounding poly it exist
        """
        properties = bounding_poly.get("property", {})
        if properties:
            languages = properties.get("detectedLanguages", [])
            if languages:
                return languages[0]['languageCode']
        return ""

    
    def get_language_code_ann(self, bounding_poly, char_walker):
        """Annotate language code of the poly's language is not tibetan

        Args:
            bounding_poly (bbox): bbox object

        Returns:
            str: text annotated with language code
        """
        ann = {}
        if bounding_poly.language != "bo":
            return None, char_walker + len(bounding_poly.text)
        else:
            end = char_walker + len(bounding_poly.text)
            span = Span(start=char_walker, end=end)
            uuid = self.get_unique_id()
            low_conf_ann = Language(span=span, language=bounding_poly.language)
            ann[uuid] = low_conf_ann
            return ann, end

    def get_lines(self, bounding_polys):
        """Return list of lines in page using bounding polys of page

        Args:
            bounding_polys (list): list of all the bounding polys

        Returns:
            list: list of lines in page
        """
        lines = []
        cur_line_polys = []
        prev_bounding_poly = bounding_polys[0]
        avg_line_height = self.get_avg_bounding_poly_height(bounding_polys)
        for bounding_poly in bounding_polys:
            if self.is_in_cur_line(prev_bounding_poly, bounding_poly, avg_line_height):
                cur_line_polys.append(bounding_poly)
            else:
                lines.append(cur_line_polys)
                cur_line_polys  = []
                cur_line_polys.append(bounding_poly)
            prev_bounding_poly = bounding_poly
        if cur_line_polys:
            lines.append(cur_line_polys)
        return lines

    def find_centriod(self, bounding_poly):
        """Calculate centriod of bounding poly

        Args:
            bounding_poly (dict): info regarding bounding poly such as vertices and description

        Returns:
            list: centriod coordinates
        """
        sum_of_x = 0
        sum_of_y = 0
        for vertice in bounding_poly.vertices:
            sum_of_x += vertice[0]
            sum_of_y += vertice[1]
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

    def has_space_attached(self, symbol):
        """Checks if symbol has space followed by it or not

        Args:
            symbol (dict): symbol info

        Returns:
            boolean: True if the symbol has space followed by it
        """
        if ('property' in symbol and 
                'detectedBreak' in symbol['property'] and 
                'type' in symbol['property']['detectedBreak'] and 
                symbol['property']['detectedBreak']['type'] == "SPACE"):
            return True
        return False
    
    def extract_vertices(self, word):
        """Extract vertices of bounding poly

        Args:
            word (dict): bounding poly info of a word

        Returns:
            list: list of vertices coordinates
        """
        vertices = []
        for vertice in word['boundingBox']['vertices']:
            vertices.append([vertice['x'], vertice['y']])
        return vertices

    def dict_to_bbox(self, word):
        """Convert bounding poly to BBox object

        Args:
            word (dict): bounding poly of a word infos

        Returns:
            obj: BBox object of bounding poly
        """
        text = word.get('text', '')
        confidence = word.get('confidence', 0.0)
        language = self.get_language_code(word)
        vertices = self.extract_vertices(word)
        bbox = BBox(text=text, vertices=vertices, confidence=confidence, language=language)
        return bbox

    def get_char_base_bounding_polys(self, response):
        """Return bounding polys in page response

        Args:
            response (dict): google ocr output of a page

        Returns:
            list: list of BBox object which saves required info of a bounding poly
        """
        bounding_polys = []
        cur_word = ""
        for page in response['fullTextAnnotation']['pages']:
            for block in page['blocks']:
                for paragraph in block['paragraphs']:
                    for word in paragraph['words']:
                        for symbol in word['symbols']:
                            cur_word += symbol['text']
                            if self.has_space_attached(symbol):
                                cur_word += " "
                        word['text'] = cur_word
                        cur_word = ""
                        bbox = self.dict_to_bbox(word)
                        bounding_polys.append(bbox)
        return bounding_polys

    def populate_confidence(self, bounding_polys):
        """Populate confidence of bounding polys of pecha level and image group level

        Args:
            bounding_polys (list): list of bounding polys
        """
        for bounding_poly in bounding_polys:
            self.word_confidences.append(float(bounding_poly.confidence))
            self.cur_base_word_confidences.append(float(bounding_poly.confidence))
    
    def get_space_poly_vertices(self, cur_bounding_poly, next_poly):
        """Return space bounding poly's vertices of located in between given polys

        Args:
            cur_bounding_poly (bbox): first bbox obj
            next_poly (bbox): second bbox obj

        Returns:
            list: list of vertices of space poly located in between
        """
        vertices = [
            cur_bounding_poly.vertices[1],
            next_poly.vertices[0],
            next_poly.vertices[3],
            cur_bounding_poly.vertices[2],
        ]
        return vertices
        
    def has_space_after(self, cur_bounding_poly, next_poly, avg_char_width):
        """Checks if there is space between two poly or not if yes returns a space poly bbox object

        Args:
            cur_bounding_poly (bbox): first bbox
            next_poly (bbox): second bbox
            avg_char_width (float): avg width of char in page

        Returns:
            bbox or none: space bbox object
        """
        cur_poly_top_right_corner = cur_bounding_poly.vertices[1][0]
        next_poly_top_left_corner = next_poly.vertices[0][0]
        if next_poly_top_left_corner - cur_poly_top_right_corner > avg_char_width*0.75 and " " not in cur_bounding_poly.text:
            space_poly_vertices = self.get_space_poly_vertices(cur_bounding_poly, next_poly)
            space_box = BBox(
                text=" ",
                vertices=space_poly_vertices,
                confidence=1.0,
                language=""
            )
            return space_box
        return None
    
    def insert_space_bounding_poly(self, bounding_polys, avg_char_width):
        """Inserts space bounding poly if missing

        Args:
            bounding_polys (list): list of bbox objects
            avg_char_width (float): avg width of char

        Returns:
            list: list of bbox objects
        """
        new_bounding_polys = []
        for poly_walker, cur_bounding_poly in enumerate(bounding_polys):
            if poly_walker == len(bounding_polys)-1:
                new_bounding_polys.append(cur_bounding_poly)
            else:
                next_poly = bounding_polys[poly_walker+1]
                space_poly = self.has_space_after(cur_bounding_poly, next_poly, avg_char_width)
                if space_poly:
                    new_bounding_polys.append(cur_bounding_poly)
                    new_bounding_polys.append(space_poly)
                else:
                    new_bounding_polys.append(cur_bounding_poly)
        return new_bounding_polys
    
    def is_tibetan(self, symbol):
        """Checks if symbol content tibetan character

        Args:
            symbol (dict): symbol info

        Returns:
            boolean: True if character is Tibetan
        """
        if re.search("\u0F00-\u0FDA", symbol['text']):
            return True
        return False
    
    def is_non_consonant(self, symbol):
        """Checks if tibetan character is Tibetan consonant or not

        Args:
            symbol (dict): symbol info

        Returns:
            boolean: True if character is tibetan consonant
        """
        if re.search('[ཀ-ཨ]', symbol['text']):
            return False
        return True

    def get_avg_char_width(self, response):
        """Calculate average width of box in a page, ignoring non consonant tibetan char

        Args:
            response (dict): ocr output of a page

        Returns:
            float: average box width in which character are saved
        """
        widths = []
        for page in response['fullTextAnnotation']['pages']:
            for block in page['blocks']:
                for paragraph in block['paragraphs']:
                    for word in paragraph['words']:
                        for symbol in word['symbols']:
                            if self.is_tibetan(symbol) and self.is_non_consonant(symbol):
                                continue
                            vertices = symbol['boundingBox']['vertices']
                            x1 = vertices[0]['x']
                            x2 = vertices[1]['x']
                            width = x2-x1
                            widths.append(width)
        return sum(widths) / len(widths)
    
    def get_base_page(self, line_wise_poly):
        base_page = ""
        for line in line_wise_poly:
            for poly in line:
                base_page += poly.text
            base_page += "\n"
        return base_page

    def post_process_page(self, page):
        """parse page response to generate page content by reordering the bounding polys

        Args:
            page (dict): page content response given by google ocr engine

        Returns:
            dict: base page, low confidence annotated page and language code annotated page 
        """
        post_processed_pages = {
            'base_page': '',
            'line_wise_poly': []
        }
        postprocessed_page_content = ""
        try:
            page_content = page["textAnnotations"][0]["description"]
        except Exception:
            print("Page empty!!")
            return postprocessed_page_content
        avg_char_width = self.get_avg_char_width(page)
        bounding_polys = self.get_char_base_bounding_polys(page)
        self.populate_confidence(bounding_polys)
        sorted_bounding_polys = self.sort_bounding_polys(bounding_polys)
        sorted_bounding_polys = self.insert_space_bounding_poly(sorted_bounding_polys, avg_char_width)
        lines = self.get_lines(sorted_bounding_polys)
        base_page = self.get_base_page(lines)
        post_processed_pages["base_page"] = base_page
        post_processed_pages["line_wise_poly"] = lines
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
        result[LayerEnum.low_conf_box.value] = json.loads(ExtentedLayer(annotation_type=LayerEnum.low_conf_box, annotations=layers["low_conf_anns"]).json(exclude_none=True))
        result[LayerEnum.language.value] = json.loads(ExtentedLayer(annotation_type=LayerEnum.language, annotations=layers["language_code_anns"]).json(exclude_none=True))

        return result

    def _get_page(self, response):
        pages = {
            'base_page': '',
            'line_wise_poly': [],
        }
        try:
            if len(response["textAnnotations"]) != 0:
                page = response["textAnnotations"][0]
            else:
                return pages
        except KeyError:
            return pages

        pages = self.post_process_page(response)

        return pages 

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

    # replace to test offline
    def _get_image_list(self, bdrc_scan_id, image_group_id):
        il = get_image_list(bdrc_scan_id, image_group_id)
        img2seq = {}
        for i, img in enumerate(il, start=1):
            name, ext = img["filename"].split(".")
            img2seq[name] = {"num": i, "ext": ext}
        return img2seq

    def get_low_conf_anns(self, line_wise_poly, last_pg_idx, is_first_pg):
        char_walker = last_pg_idx
        if not is_first_pg:
            char_walker += self.n_page_breaker_char
        anns = {}
        cur_ann = {}
        for line in line_wise_poly:
            for poly in line:
                cur_ann, char_walker = self.get_low_confidence_ann(poly, char_walker)
                if cur_ann:
                    anns.update(cur_ann)
            char_walker += 1
        return anns
    
    def get_language_code_anns(self, line_wise_poly, last_pg_idx, is_first_pg):
        char_walker = last_pg_idx
        if not is_first_pg:
            char_walker += self.n_page_breaker_char
        anns = {}
        cur_ann = {}
        for line in line_wise_poly:
            for poly in line:
                cur_ann, char_walker = self.get_language_code_ann(poly, char_walker)
                if cur_ann:
                    anns.update(cur_ann)
            char_walker += 1
        return anns

    def build_layers(self, responses, image_group_id, base_id=None):
        base_pages = []
        low_conf_anns = {}
        language_code_anns = {}
        pages_ref = []
        last_pg_end_idx = 0
        char_walker = 0
        img2seq = self._get_image_list(self.bdrc_scan_id, image_group_id)
        for response, page_ref in responses:
            n_pg = img2seq[page_ref]["num"]

            # extract annotation
            if not response:
                logging.error(f"Failed : {n_pg}")
                continue
            pages = self._get_page(response)
            base_page = pages['base_page']

            # skip empty page (can be bad image)
            if not base_page:
                logging.error(f"empty page {n_pg}")
                continue
            lines, last_pg_end_idx = self._get_lines(base_page, last_pg_end_idx, n_pg == 1)
            base_pages.append((lines[0][0], lines[-1][1], n_pg))
            pages_ref.append(f"{page_ref}.{img2seq[page_ref]['ext']}")

            # create base_text
            self.base_text.append(base_page)
            cur_page_low_conf_anns = self.get_low_conf_anns(pages['line_wise_poly'], char_walker, n_pg == 1)
            cur_page_lang_code_anns = self.get_language_code_anns(pages['line_wise_poly'], char_walker, n_pg == 1)
            char_walker = last_pg_end_idx
            low_conf_anns.update(cur_page_low_conf_anns)
            language_code_anns.update(cur_page_lang_code_anns)

        result = {
            "base_pages": base_pages,
            "pages_ref": pages_ref,
            "low_conf_anns": low_conf_anns,
            "language_code_anns": language_code_anns
            }

        return result

    def get_base_text(self):
        base_text = f"{self.page_break}".join(self.base_text)
        self.base_text = []

        return base_text

    def get_copyright_and_license_info(self, bdata):
        if "copyright_status" not in bdata["source_metadata"]:
            return {}, None
        cs = bdata["source_metadata"]["copyright_status"]
        if cs == "http://purl.bdrc.io/resource/CopyrightPublicDomain":
            return Copyright_public_domain, LicenseType.CC0
        if cs == "http://purl.bdrc.io/resource/CopyrightUndetermined":
            return Copyright_unknown, None
        return Copyright_copyrighted, LicenseType.UNDER_COPYRIGHT
            
    def get_metadata(self, pecha_id, ocr_import_info):

        source_metadata = {
            "id": f"http://purl.bdrc.io/resource/{self.bdrc_scan_id}",
            "title": "",
            "author": "",
        }
        copyright = {}
        license = None
        if self.buda_data is not None:
            source_metadata = self.buda_data["source_metadata"]
            copyright, license = self.get_copyright_and_license_info(self.buda_data)

        metadata = InitialPechaMetadata(
            source='https://library.bdrc.io',
            initial_creation_type=InitialCreationType.ocr,
            imported=datetime.datetime.now(timezone.utc),
            last_modified=datetime.datetime.now(timezone.utc),
            parser=None,
            copyright=copyright,
            license=license,
            source_metadata=source_metadata,
            default_language=self.default_language,
            ocr_import_info=ocr_import_info
        )
        return json.loads(metadata.json())

    def get_base_confidence_median(self):
        cur_base_confidences = self.cur_base_word_confidences
        base_confidence_median = statistics.median(cur_base_confidences)
        return base_confidence_median
    
    def get_base_confidence_mean(self):
        cur_base_confidences = self.cur_base_word_confidences
        base_confidence_mean = statistics.mean(cur_base_confidences)
        return base_confidence_mean

    def set_base_meta(self, image_group_id, base_file_name):
        base_confidence_median = self.get_base_confidence_median()
        base_confidence_mean = self.get_base_confidence_mean()
        self.cur_word_confidences = []
        self.base_meta[base_file_name] = {
            "source_metadata": self.buda_data["image_groups"][image_group_id],
            "order": self.buda_data["image_groups"][image_group_id]["volume_number"],
            "base_file": f"{base_file_name}.txt",
            "statistics": {
              "ocr_word_median_confidence_index": base_confidence_median,
              "ocr_word_mean_confidence_index": base_confidence_mean
            }
        }

    @staticmethod
    def image_group_to_folder_name(scan_id, image_group_id):
        image_group_folder_part = image_group_id
        pre, rest = image_group_id[0], image_group_id[1:]
        if pre == "I" and rest.isdigit() and len(rest) == 4:
            image_group_folder_part = rest
        return scan_id+"-"+image_group_folder_part
    
    def create_opf(self, input_path, pecha_id, ocr_import_info = {}, buda_data = None):
        """Create opf of google ocred pecha

        Args:
            input_path (str): input path, local folder expected to match the output/ folder on s3, ex:
                              s3://ocr.bdrc.io/Works/60/W22084/vision/batch001/output/
            pecha_id (str): pecha id
            ocr_import_info (Dict): an object with the following keys:
                bdrc_scan_id: str
                source: str
                ocr_info: Dict
                batch_id: str
                software_id: str
                expected_default_language: str

        Returns:
            path: opf path
        """
        # we assume that
        input_path = Path(input_path)

        # if the bdrc scan id is not specified, we assume it's the directory namepecha_id
        self.bdrc_scan_id = input_path.name if "bdrc_scan_id" not in ocr_import_info else ocr_import_info["bdrc_scan_id"]
        
        self._build_dirs(input_path, id_=pecha_id)

        if buda_data is None:
            self.buda_data = get_buda_scan_info(self.bdrc_scan_id)
        else:
            self.buda_data = buda_data
        self.default_language = "bo" if "expected_default_language" not in ocr_import_info else ocr_import_info["expected_default_language"]

        self.metadata = self.get_metadata(pecha_id, ocr_import_info)

        for image_group_id, image_group_info in self.buda_data["image_groups"].items():
            vol_folder = GoogleOCRFormatter.image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
            if not (input_path / vol_folder).is_dir():
                logging.warn("no folder for image group "+str(input_path / vol_folder)+" (nb of images in theory: "+str(image_group_info["total_pages"])+")")
                continue
            base_id = image_group_id
            responses = self.get_input(input_path / vol_folder)
            layers = self.build_layers(responses, image_group_id, base_id)
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
            self.set_base_meta(image_group_id, base_id)

        # we add the rest to metadata:
        self.metadata["bases"] = self.base_meta
        self.metadata['statistics'] = {
            "ocr_word_mean_confidence_index": statistics.mean(self.word_confidences),
            "ocr_word_median_confidence_index": statistics.median(self.word_confidences)
        }

        meta_fn = self.dirs["opf_path"] / "meta.yml"
        dump_yaml(self.metadata, meta_fn)

        return self.dirs["opf_path"].parent


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf("../../Esukhia/img2opf/archive/output/W1PD95844", 300)
