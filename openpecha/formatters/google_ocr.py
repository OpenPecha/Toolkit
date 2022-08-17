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
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType, LicenseType, Copyright_copyrighted, Copyright_unknown, Copyright_public_domain
from openpecha.formatters import BaseFormatter
from openpecha.utils import dump_yaml, gzip_str

from openpecha.buda.api import get_buda_scan_info, get_image_list

ANNOTATION_MINIMAL_LEN = 20
ANNOTATION_MINIMAL_CONFIDENCE = 0.9

extended_LayerEnum = [(l.name, l.value) for l in LayerEnum] + [("low_conf_box", "OCRConfidence")]
LayerEnum = Enum("LayerEnum", extended_LayerEnum)

class ExtentedLayer(Layer):
    annotation_type: LayerEnum

class OCRConfidence(BaseAnnotation):
    confidence: float

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

    def get_poly_lines(self, bounding_polys):
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
        if next_poly_top_left_corner - cur_poly_top_right_corner > avg_char_width*0.75 and cur_bounding_poly.text[-1] not in [' ', '་']:
            space_poly_vertices = self.get_space_poly_vertices(cur_bounding_poly, next_poly)
            space_box = BBox(
                text=" ",
                vertices=space_poly_vertices,
                confidence=1.0,
                language=cur_bounding_poly.language
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
    
    def is_tibetan_non_consonant(self, symbol):
        """Checks if tibetan character is Tibetan but not a consonant

        Args:
            symbol (dict): symbol info

        Returns:
            boolean: True if character is Tibetan non-consonant
        """
        # we assume there is just one character:
        c = ord(symbol['text'][0])
        if (c >= ord('ༀ') and c <= ord('༿')) or (c >= ord('ཱ') and c <= ord('࿚')):
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
                            if self.is_tibetan_non_consonant(symbol):
                                continue
                            vertices = symbol['boundingBox']['vertices']
                            x1 = vertices[0]['x']
                            x2 = vertices[1]['x']
                            width = x2-x1
                            widths.append(width)
        return sum(widths) / len(widths)

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
                            if symbol.get("confidence", 1) < ANNOTATION_MINIMAL_CONFIDENCE:
                                low_conf_chars += f'{symbol["text"]} {char_idx}\n'
                            char_idx += 1
        if low_conf_chars:
            path.write_bytes(gzip_str(low_conf_chars))

    # replace to test offline
    def _get_image_list(self, bdrc_scan_id, image_group_id):
        return get_image_list(bdrc_scan_id, image_group_id)

    def get_language_code(self, poly):
        lang = ""
        properties = poly.get("property", {})
        if properties:
            languages = properties.get("detectedLanguages", [])
            if languages:
                lang = languages[0]['languageCode']
        if lang == "":
            return self.default_language
        if lang in ["bo", "en", "zh"]:
            return lang
        if lang == "dz":
            return "bo"
        # English is a kind of default for our purpose
        return "en"

    def add_language(self, poly, poly_start_cc, state):
        poly_lang = poly.language
        previous_ann = state["latest_language_annotation"]
        poly_end_cc = state["base_layer_len"] # by construction
        if previous_ann is not None:
            # if poly has the same language as the latest annotation, we just lengthen the previous
            # annotation to include this poly:
            if poly_lang == previous_ann['lang']:
                previous_ann["end"] = poly_end_cc
                return
            # if poly is the default language, we just conclude the previous annotation
            if poly_lang == self.default_language:
                state["latest_language_annotation"] = None
                return
            # else, we create a new annotation
            annotation = {"start": poly_start_cc, "end": poly_end_cc, "lang": poly_lang}
            state["language_annotations"].append(annotation)
            state["latest_language_annotation"] = annotation
            return
        # if there's no previous annotation and language is the default language, return
        if poly_lang == self.default_language:
            return
        # if there's no previous annotation and language is not the default, we create an annotation
        annotation = {"start": poly_start_cc, "end": poly_end_cc, "lang": poly_lang}
        state["language_annotations"].append(annotation)
        state["latest_language_annotation"] = annotation

    def add_low_confidence(self, poly, poly_start_cc, state):
        if poly.confidence > ANNOTATION_MINIMAL_CONFIDENCE:
            state["latest_low_confidence_annotation"] = None
            return
        poly_end_cc = state["base_layer_len"] # by construction
        if state["latest_low_confidence_annotation"] is not None:
            # average of the confidence indexes, weighted by character length
            state["latest_low_confidence_annotation"]["weights"].append((poly_end_cc - poly_start_cc, poly.confidence))
            state["latest_low_confidence_annotation"]["end"] = poly_end_cc
        else:
            annotation = {"start": poly_start_cc, "end": poly_end_cc, 
                "weights": [(poly_end_cc - poly_start_cc, poly.confidence)]}
            state["page_low_confidence_annotations"].append(annotation)
            state["latest_low_confidence_annotation"] = annotation

    def build_page(self, ocr_object, image_number, imageinfo, state):
        try:
            page_content = ocr_object["textAnnotations"][0]["description"]
        except Exception:
            logging.error("OCR page is empty (no textAnnotations[0]/description)")
            return
        avg_char_width = self.get_avg_char_width(ocr_object)
        bounding_polys = self.get_char_base_bounding_polys(ocr_object)
        sorted_bounding_polys = self.sort_bounding_polys(bounding_polys)
        sorted_bounding_polys = self.insert_space_bounding_poly(sorted_bounding_polys, avg_char_width)
        poly_lines = self.get_poly_lines(sorted_bounding_polys)
        page_start_cc = state["base_layer_len"]
        page_word_confidences = []
        for poly_line in poly_lines:
            for poly in poly_line:
                state["base_layer"] += poly.text
                start_cc = state["base_layer_len"]
                state["base_layer_len"] += len(poly.text)
                state["word_confidences"].append(float(poly.confidence))
                page_word_confidences.append(float(poly.confidence))
                self.add_language(poly, start_cc, state)
                self.add_low_confidence(poly, start_cc, state)
            # adding a line break at the end of a line
            state["base_layer"] += "\n"
            state["base_layer_len"] += 1
        # if the whole page is below the min confidence level, we just add one
        # annotation for the page instead of annotating each word
        mean_page_confidence = statistics.mean(page_word_confidences)
        if statistics.mean(page_word_confidences) < ANNOTATION_MINIMAL_CONFIDENCE:
            state["low_confidence_annotations"][self.get_unique_id()] = OCRConfidence(
                span=Span(start=page_start_cc, end=state["base_layer_len"]), 
                confidence=mean_page_confidence)
        else:
            self.merge_low_confidence_annotations(state["page_low_confidence_annotations"], state["low_confidence_annotations"])
            state["page_low_confidence_annotations"] = []
        # add pagination annotation:
        state["pagination_annotations"][self.get_unique_id()] = Page(
            span=Span(start=page_start_cc, end=state["base_layer_len"]), 
            imgnum=image_number, 
            reference=imageinfo["filename"])
        # adding another line break at the end of a page
        state["base_layer"] += "\n"
        state["base_layer_len"] += 1

    def confidence_index_from_weighted_list(self, weights):
        sum_weights = 0
        confidence_sum = 0
        for weight, confidence in weights:
            sum_weights += weight
            confidence_sum += weight * confidence
        return confidence_sum / sum_weights

    def merge_low_confidence_annotations(self, annotation_list_src, annotations_dst):
        for annotation in annotation_list_src:
            average_confidence = self.confidence_index_from_weighted_list(annotation["weights"])
            annotation = OCRConfidence(
                span = Span(start=annotation["start"], end=annotation["end"]),
                confidence = average_confidence)
            annotations_dst[self.get_unique_id()] = annotation

    def merge_short_language_annotations(self, annotation_list):
        annotations = {}
        previous_annotation = None
        # annotation list is in span order
        for annotation in annotation_list:
            if annotation['end'] - annotation['start'] < ANNOTATION_MINIMAL_LEN:
                if previous_annotation is not None and annotation['start'] - previous_annotation.span.end < ANNOTATION_MINIMAL_LEN:
                    previous_annotation.span.end = annotation['end']
                continue
            if previous_annotation is not None and annotation["lang"] == previous_annotation.language:
                if annotation['start'] - previous_annotation.span.end < ANNOTATION_MINIMAL_LEN:
                    previous_annotation.span.end = annotation['end']
                    continue
            previous_annotation = Language(
                span = Span(start=annotation["start"], end=annotation["end"]),
                language = annotation["lang"])
            annotations[self.get_unique_id()] = previous_annotation
        return annotations

    def build_base(self, image_group_id, image_group_ocr_path):
        """ The main function that takes the OCR results for an entire volume
            and creates its base and layers
        """
        image_list = self._get_image_list(self.bdrc_scan_id, image_group_id)
        state = {
            "base_layer_len": 0,
            "base_layer": "",
            "low_confidence_annotations": {},
            "language_annotations": [],
            "pagination_annotations": {},
            "word_confidences": [],
            "latest_language_annotation": None,
            "latest_low_confidence_annotation": None,
            "page_low_confidence_annotations": []
        }
        for image_number, imginfo in enumerate(image_list):
            image_filename = imginfo["filename"]
            expected_ocr_filename = image_filename[:image_filename.rfind('.')]+".json.gz"
            expected_ocr_path = image_group_ocr_path / expected_ocr_filename
            if not expected_ocr_path.is_file():
                logging.warning("could not find "+str(expected_ocr_path))
                continue
            ocr_object = None
            try:
                ocr_object = json.load(gzip.open(str(expected_ocr_path), "rb"))
            except:
                logging.error("could not read "+str(expected_ocr_path))
                continue
            # enumerate starts at 0 but image numbers start at 1
            self.build_page(ocr_object, image_number+1, imginfo, state)
        layers = {}
        if state["pagination_annotations"]:
            layer = ExtentedLayer(annotation_type=LayerEnum.pagination, annotations=state["pagination_annotations"])
            layers[LayerEnum.pagination.value] = json.loads(layer.json(exclude_none=True))
        if state["language_annotations"]:
            annotations = self.merge_short_language_annotations(state["language_annotations"])
            layer = ExtentedLayer(annotation_type=LayerEnum.language, annotations=annotations)
            layers[LayerEnum.language.value] = json.loads(layer.json(exclude_none=True))
        if state["low_confidence_annotations"]:
            layer = ExtentedLayer(annotation_type=LayerEnum.low_conf_box, annotations=state["low_confidence_annotations"])
            layers[LayerEnum.low_conf_box.value] = json.loads(layer.json(exclude_none=True))

        return state["base_layer"], layers, state["word_confidences"]

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
            id=pecha_id,
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

    def set_base_meta(self, image_group_id, base_file_name, word_confidence_list):
        self.cur_word_confidences = []
        self.base_meta[base_file_name] = {
            "source_metadata": self.buda_data["image_groups"][image_group_id],
            "order": self.buda_data["image_groups"][image_group_id]["volume_number"],
            "base_file": f"{base_file_name}.txt",
            "statistics": {
              "ocr_word_median_confidence_index": statistics.median(word_confidence_list),
              "ocr_word_mean_confidence_index": statistics.mean(word_confidence_list)
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
        total_word_confidence_list = []

        for image_group_id, image_group_info in self.buda_data["image_groups"].items():
            vol_folder = GoogleOCRFormatter.image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
            if not (input_path / vol_folder).is_dir():
                logging.warn("no folder for image group "+str(input_path / vol_folder)+" (nb of images in theory: "+str(image_group_info["total_pages"])+")")
                continue
            base_id = image_group_id
            base_text, layers, word_confidence_list = self.build_base(image_group_id, (input_path / vol_folder))

            # save base_text
            (self.dirs["opf_path"] / "base" / f"{base_id}.txt").write_text(base_text)

            # save layers
            vol_layer_path = self.dirs["layers_path"] / base_id
            vol_layer_path.mkdir(exist_ok=True)
            for layer_id, layer in layers.items():
                layer_fn = vol_layer_path / f"{layer_id}.yml"
                dump_yaml(layer, layer_fn)
            self.set_base_meta(image_group_id, base_id, word_confidence_list)
            total_word_confidence_list += word_confidence_list

        # we add the rest to metadata:
        self.metadata["bases"] = self.base_meta
        self.metadata['statistics'] = {
            # there are probably more efficient ways to compute those
            "ocr_word_mean_confidence_index": statistics.mean(total_word_confidence_list),
            "ocr_word_median_confidence_index": statistics.median(total_word_confidence_list)
        }

        meta_fn = self.dirs["opf_path"] / "meta.yml"
        dump_yaml(self.metadata, meta_fn)

        return self.dirs["opf_path"].parent


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf("../../Esukhia/img2opf/archive/output/W1PD95844", 300)
