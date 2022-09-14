from pydoc import pager
import re
from enum import Enum
from pathlib import Path

import json
import logging
import datetime
import statistics
from datetime import timezone
from bs4 import BeautifulSoup

from openpecha.core.annotation import Page, Span
from openpecha.core.annotations import BaseAnnotation, Language, OCRConfidence
from openpecha.core.layer import Layer, LayerEnum, OCRConfidenceLayer
from openpecha.core.ids import get_base_id
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType, LicenseType, Copyright_copyrighted, Copyright_unknown, Copyright_public_domain
from openpecha.formatters import BaseFormatter

from openpecha.formatters.ocr.ocr import OCRFormatter, BBox

# from openpecha.core.annotation import Page, Span
from openpecha.utils import load_yaml, dump_yaml, gzip_str
# from openpecha.formatters.google_vision import GoogleVisionFormatter, GoogleVisionBDRCFileProvider
from openpecha.buda.api import get_buda_scan_info, get_image_list, image_group_to_folder_name

ANNOTATION_MINIMAL_LEN = 20
ANNOTATION_MINIMAL_CONFIDENCE = 0.8
ANNOTATION_MAX_LOW_CONF_PER_PAGE = 10
NOISE_PATTERN = re.compile(r'(?:\s|[-，.… }#*,+•：/|(©:;་"།=@%༔){"])+')
GOOGLE_OCR_IMPORT_VERSION = "1.0.0"


extended_LayerEnum = [(l.name, l.value) for l in LayerEnum] + [("low_conf_box", "LowConfBox")]
LayerEnum = Enum("LayerEnum", extended_LayerEnum)

class ExtentedLayer(Layer):
    annotation_type: LayerEnum

class LowConfBox(BaseAnnotation):
    confidence: str


class HOCRBDRCFileProvider():
    def __init__(self, bdrc_scan_id, buda_data, ocr_import_info, ocr_disk_path=None):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.images_info = {}
    
    def get_image_file_list(self, image_group_id):
        image_list = []
        file_list = []
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        info_path = Path(f"{self.ocr_disk_path}/google_books/batch_2022/info/{vol_folder}/gb-bdrc-map.json")
        self.images_info[image_group_id] = load_yaml(info_path)
        file_paths = list(Path(f"{self.ocr_disk_path}/google_books/batch_2022/output/{vol_folder}").iterdir())
        for file_path in file_paths:
            if file_path.name[-4:] == "html":
                file_list.append(file_path.name[:-5])
        for file_name, img_ref in self.images_info[image_group_id].items():
            if file_name in file_list:
                image_list.append(file_name)
        return image_list

    def get_source_info(self):
        return self.buda_data
    
    def get_image_bounding_polys(self, image_group_id, image_filename):
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        image_hocr_path = Path(f"{self.ocr_disk_path}/google_books/batch_2022/output/{vol_folder}/{image_filename}.html")
        bounding_polys = None
        try:
            parser = HOCRParser()
            bounding_polys = parser.parse_hocr(image_hocr_path)
        except Exception as e:
            logging.exception("could not read "+str(image_hocr_path))
            print(e)
        return bounding_polys

class HOCRParser():
    def __init__(self):
        self.word_span = 0
        
    def get_vertices(self, word_box):
        try:
            vertices_info = word_box['title'].split(';')[0]
        except:
            return []
        vertices_list = []
        vertices_info = vertices_info.replace("bbox ", "")
        vertices_coordinates = vertices_info.split(" ")
        minX = int(vertices_coordinates[0])
        minY = int(vertices_coordinates[1])
        maxX = int(vertices_coordinates[2])
        maxY = int(vertices_coordinates[3])

        vertice_dic = {}
        vertice_dic["x"] = minX
        vertice_dic["y"] = minY
        vertices_list.append(vertice_dic)

        vertice_dic = {}
        vertice_dic["x"] = maxX
        vertice_dic["y"] = minY
        vertices_list.append(vertice_dic)

        vertice_dic = {}
        vertice_dic["x"] = maxX
        vertice_dic["y"] = maxY
        vertices_list.append(vertice_dic)

        vertice_dic = {}
        vertice_dic["x"] = minX
        vertice_dic["y"] = maxY
        vertices_list.append(vertice_dic)
        
        vertices = []
        for vertice in vertices_list:
            vertices.append([vertice.get('x', 0), vertice.get('y', 0)])
        return vertices

    def get_confidence(self, word_box):
        confidence_info = word_box['title']
        confidence = float(int(re.search("x_wconf (\d.?)", confidence_info).group(1))/100)
        return confidence

    def get_lang(self,word_box):
        langauge = word_box.get('lang', "")
        return langauge
    
    def get_word_text_with_space(self, line_text, word_box):
        text = word_box.text
        self.word_span += len(text)
        if len(line_text) == self.word_span:
            return text
        else:
            next_character = line_text[self.word_span]
            if next_character == " ":
                self.word_span += 1
                text = text + " "
        return text
        
        
    def parse_box(self, line_box, word_box, language):
        line_text = line_box.text
        vertices = self.get_vertices(word_box)
        confidence = self.get_confidence(word_box)
        text = self.get_word_text_with_space(line_text, word_box)
        box = BBox(
            text=text,
            vertices=vertices,
            confidence=confidence,
            language=language
        )
        return box


    def get_page_langugage(self, hocr_html):
        page_box = hocr_html.find_all("div", {"class": "ocr_page"})
        lang_info = page_box[0]['title']
        language = re.search("ocrp_lang (\D.?)", lang_info).group(1)
        return language 
    
    
    def get_boxes(self, hocr_html):
        boxes = []
        hocr_html = BeautifulSoup(hocr_html, 'html.parser')
        language = self.get_page_langugage(hocr_html)
        line_boxes = hocr_html.find_all("span", {"class": "ocr_line"})
        for line_box in line_boxes:
            self.word_span = 0
            word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
            for word_box in word_boxes:
                boxes.append(self.parse_box(line_box,word_box, language))
        return boxes


    def parse_hocr(self, image_hocr_path):
        hocr_html = Path(image_hocr_path).read_text(encoding='utf-8')
        bbox = self.get_boxes(hocr_html)
        return bbox


class HOCRFormatter(OCRFormatter):
    """
    OpenPecha Formatter for Google OCR HOCR output of scanned pecha.
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
        self.source_info = {}
        self.remove_non_character_lines = True
        self.create_language_layer = True
        self.ocr_confidence_threshold = ANNOTATION_MINIMAL_CONFIDENCE
        self.language_annotation_min_len = ANNOTATION_MINIMAL_LEN


    def build_page(self, bounding_polys, image_number, image_filename, state):
        if bounding_polys == []:
            logging.error("OCR page is empty (no textAnnotations[0]/description)")
            return
        sorted_bounding_polys = self.sort_bounding_polys(bounding_polys)
        # sorted_bounding_polys = self.insert_space_bounding_poly(sorted_bounding_polys, avg_char_width)
        poly_lines = self.get_poly_lines(sorted_bounding_polys)
        page_start_cc = state["base_layer_len"]
        page_word_confidences = []
        for poly_line in poly_lines:
            if self.remove_non_character_lines and not self.poly_line_has_characters(poly_line):
                continue
            for poly in poly_line:
                state["base_layer"] += poly.text
                start_cc = state["base_layer_len"]
                state["base_layer_len"] += len(poly.text)
                if poly.confidence is not None:
                    state["word_confidences"].append(float(poly.confidence))
                    page_word_confidences.append(float(poly.confidence))
                    self.add_low_confidence(poly, start_cc, state)
                self.add_language(poly, start_cc, state)
            # adding a line break at the end of a line
            state["base_layer"] += "\n"
            state["base_layer_len"] += 1
        # if the whole page is below the min confidence level, we just add one
        # annotation for the page instead of annotating each word
        if page_word_confidences:
            mean_page_confidence = statistics.mean(page_word_confidences)
        else:
            mean_page_confidence = 0
        nb_below_threshold = len(state["page_low_confidence_annotations"])
        if mean_page_confidence < self.ocr_confidence_threshold or nb_below_threshold > self.max_low_conf_per_page:
            state["low_confidence_annotations"][self.get_unique_id()] = OCRConfidence(
                span=Span(start=page_start_cc, end=state["base_layer_len"]), 
                confidence=mean_page_confidence, nb_below_threshold=nb_below_threshold)
        else:
            self.merge_page_low_confidence_annotations(state["page_low_confidence_annotations"], state["low_confidence_annotations"])
            state["page_low_confidence_annotations"] = []
        # add pagination annotation:
        state["pagination_annotations"][self.get_unique_id()] = Page(
            span=Span(start=page_start_cc, end=state["base_layer_len"]), 
            imgnum=image_number, 
            reference=image_filename)
        # adding another line break at the end of a page
        state["base_layer"] += "\n"
        state["base_layer_len"] += 1

    def build_base(self, image_group_id):
        """ The main function that takes the OCR results for an entire volume
            and creates its base and layers
        """
        image_list = self.data_provider.get_image_file_list(image_group_id)
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
        for image_filename, image_reference in self.data_provider.images_info[image_group_id].items():
            if image_filename not in image_list:
                continue
            # enumerate starts at 0 but image numbers start at 1
            bounding_polys = self.data_provider.get_image_bounding_polys(image_group_id, image_filename)
            self.build_page(bounding_polys, int(image_filename), image_reference, state)
        layers = {}
        if state["pagination_annotations"]:
            layer = Layer(annotation_type=LayerEnum.pagination.value, annotations=state["pagination_annotations"])
            layers[LayerEnum.pagination.value] = json.loads(layer.json(exclude_none=True))
        if state["language_annotations"]:
            annotations = self.merge_short_language_annotations(state["language_annotations"])
            layer = Layer(annotation_type=LayerEnum.language.value, annotations=annotations)
            layers[LayerEnum.language.value] = json.loads(layer.json(exclude_none=True))
        if state["low_confidence_annotations"]:
            layer = OCRConfidenceLayer(
                confidence_threshold=self.ocr_confidence_threshold, 
                annotations=state["low_confidence_annotations"]
            )
            layers[LayerEnum.ocr_confidence.value] = json.loads(layer.json(exclude_none=True))

        return state["base_layer"], layers, state["word_confidences"]

    
    def create_opf(self, data_provider, pecha_id, opf_options = {}, ocr_import_info = {}):
        """Create opf of google ocred pecha

        Args:
            data_provider (DataProvider): an instance that will be used to get the necessary data
            pecha_id (str): pecha id
            opf_options (Dict): an object with the following keys:
                create_language_layer: boolean
                language_annotation_min_len: int
                ocr_confidence_threshold: float (use -1.0 for no OCR confidence layer)
                remove_non_character_lines: boolean
                max_low_conf_per_page: int
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
        self.data_provider = data_provider
        self._build_dirs(None, id_=pecha_id)
        
        self.remove_non_character_lines = opf_options["remove_non_character_lines"] if "remove_non_character_lines" in opf_options else True
        self.create_language_layer = opf_options["create_language_layer"] if "create_language_layer" in opf_options else True
        self.ocr_confidence_threshold = opf_options["ocr_confidence_threshold"] if "ocr_confidence_threshold" in opf_options else ANNOTATION_MINIMAL_CONFIDENCE
        self.language_annotation_min_len = opf_options["language_annotation_min_len"] if "language_annotation_min_len" in opf_options else ANNOTATION_MINIMAL_LEN
        self.max_low_conf_per_page = opf_options["max_low_conf_per_page"] if "max_low_conf_per_page" in opf_options else ANNOTATION_MAX_LOW_CONF_PER_PAGE

        # if the bdrc scan id is not specified, we assume it's the directory namepecha_id
        self.bdrc_scan_id = ocr_import_info["bdrc_scan_id"]
        self.source_info = data_provider.get_source_info()
        self.default_language = "bo" if "expected_default_language" not in ocr_import_info else ocr_import_info["expected_default_language"]
        self.default_language = "bo"
        if "expected_default_language" in ocr_import_info:
            self.default_language = ocr_import_info["expected_default_language"]
        elif "languages" in buda_data and buda_data["languages"]:
            self.default_language = buda_data["languages"][0]

        # self.metadata = self.get_metadata(pecha_id, ocr_import_info)
        total_word_confidence_list = []
        for image_group_id, image_group_info in self.source_info["image_groups"].items():
            if image_group_info['volume_number'] in [1,2]: 
                base_id = image_group_id
                base_text, layers, word_confidence_list = self.build_base(image_group_id)
            else:
                continue

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
        if total_word_confidence_list:
            self.metadata['statistics'] = {
                # there are probably more efficient ways to compute those
                "ocr_word_mean_confidence_index": statistics.mean(total_word_confidence_list),
                "ocr_word_median_confidence_index": statistics.median(total_word_confidence_list)
            }

        meta_fn = self.dirs["opf_path"] / "meta.yml"
        # dump_yaml(self.metadata, meta_fn)

        return self.dirs["opf_path"].parent



def get_ocr_import_info(work_id, batch, ocr_disk_path):
    info_json = load_yaml(Path(f"{ocr_disk_path}/google_books/{batch}/info.json"))
    ocr_import_info ={
        "source": "bdrc",
        "software": "google_books",
        "batch": batch,
        "expected_default_language": "bo",
        "bdrc_scan_id": work_id,
        "ocr_info": {
            "timestamp": info_json['timestamp']
        }
    }
    return ocr_import_info




if __name__ == "__main__":
    work_id = "W2PD17457"
    pecha_id = "I1234567"
    output_path = Path(f"./")
    ocr_disk_path = Path(f"./tests/formatters/hocr/data/W2PD17457/")
    buda_data = get_buda_scan_info(work_id)
    ocr_import_info = get_ocr_import_info(work_id, "batch_2022", ocr_disk_path)
    data_provider = HOCRBDRCFileProvider(work_id, buda_data, ocr_import_info, ocr_disk_path) 
    formatter = HOCRFormatter(output_path)
    formatter.create_opf(data_provider, pecha_id, opf_options={}, ocr_import_info=ocr_import_info)