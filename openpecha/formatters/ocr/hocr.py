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

    def get_image_data(self, image_group_id, image_filename)
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        image_hocr_path = Path(self.ocr_disk_path) / {vol_folder} / Path(f"{image_filename}.html")
        hocr_html = image_hocr_path.read_text(encoding='utf-8')
        return hocr_html
    
class HOCRFormatter(OCRFormatter):
    """
    OpenPecha Formatter for Google OCR HOCR output of scanned pecha.
    """
    def __init__(self):
        self.word_span = 0

    def get_confidence(self, word_box):
        confidence_info = word_box['title']
        confidence = float(int(re.search(r"x_wconf (\d+)", confidence_info).group(1))/100)
        return confidence

    def get_lang(self, word_box):
        language = word_box.get('lang', "")
        return language
    
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
        try:
            vertices_info = word_box['title'].split(';')[0]
        except:
            return None
        vertices_coordinates = vertices_info.split(" ")
        x1 = int(vertices_coordinates[1])
        y1 = int(vertices_coordinates[2])
        x2 = int(vertices_coordinates[3])
        y2 = int(vertices_coordinates[4])
        confidence = self.get_confidence(word_box)
        text = self.get_word_text_with_space(line_text, word_box)
        box = BBox(x1, x2, y1, y2,
            text=text,
            vertices=vertices,
            confidence=confidence,
            language=language
        )
        return box

    def get_page_language(self, hocr_html):
        page_box = hocr_html.find_all("div", {"class": "ocr_page"})
        lang_info = page_box[0]['title']
        language = re.search(r"ocrp_lang ([a-z]+)", lang_info).group(1)
        return language 
    
    def get_boxes(self, hocr_page_html):
        boxes = []
        hocr_html = BeautifulSoup(hocr_html, 'html.parser')
        language = self.get_page_language(hocr_html)
        line_boxes = hocr_html.find_all("span", {"class": "ocr_line"})
        for line_box in line_boxes:
            self.word_span = 0
            word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
            for word_box in word_boxes:
                boxes.append(self.parse_box(line_box,word_box, language))
        return boxes

    def get_bboxes_for_page(self, image_group_id, image_filename):
        hocr_page_html = self.data_provider.get_image_data(image_group_id, image_filename)
        bboxes = self.get_boxes(hocr_page_html)
        return bboxes


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