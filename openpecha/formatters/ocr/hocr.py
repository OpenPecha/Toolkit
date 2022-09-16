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

from openpecha.formatters.ocr.ocr import OCRFormatter, BBox

# from openpecha.core.annotation import Page, Span
from openpecha.utils import load_yaml, dump_yaml, gzip_str
# from openpecha.formatters.google_vision import GoogleVisionFormatter, GoogleVisionBDRCFileProvider
from openpecha.buda.api import get_buda_scan_info, get_image_list, image_group_to_folder_name


class HOCRBDRCFileProvider():
    def __init__(self, bdrc_scan_id, buda_data, ocr_import_info, ocr_disk_path=None):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.images_info = {}
    

    def get_image_list(self, image_group_id):
        self.get_images_info(image_group_id)
        buda_il = get_image_list(self.bdrc_scan_id, image_group_id)
        # format should be a list of image_id (/ file names)
        return map(lambda ii: ii["filename"], buda_il)
    
    def get_images_info(self, image_group_id):
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        image_info_path = Path(f"{self.ocr_disk_path}") / "google_books" / "batch_2022" / "info" / vol_folder / "gb-bdrc-map.json"
        self.images_info = load_yaml(image_info_path)

    def get_source_info(self):
        return self.buda_data
    
    def get_hocr_filename(self, image_id):
        for filename, img_ref in self.images_info.items():
            img_id = img_ref
            if img_id == image_id:
                return filename

    def get_image_data(self, image_group_id, image_filename):
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        hocr_filename = self.get_hocr_filename(image_filename)
        image_hocr_path = Path(f"{self.ocr_disk_path}") / "google_books" / "batch_2022" / "output" / vol_folder / f"{hocr_filename}.html"
        hocr_html = image_hocr_path.read_text(encoding='utf-8')
        return hocr_html
    
    
class HOCRFormatter(OCRFormatter):
    """
    OpenPecha Formatter for Google OCR HOCR output of scanned pecha.
    """
    def __init__(self, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
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
        hocr_html = BeautifulSoup(hocr_page_html, 'html.parser')
        language = self.get_page_language(hocr_html)
        line_boxes = hocr_html.find_all("span", {"class": "ocr_line"})
        for line_box in line_boxes:
            self.word_span = 0
            word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
            for word_box in word_boxes:
                boxes.append(self.parse_box(line_box,word_box, language))
        return boxes

    def get_bboxes_for_page(self, image_group_id, image_filename):
        bboxes = []
        hocr_page_html = self.data_provider.get_image_data(image_group_id, image_filename)
        if hocr_page_html:
            bboxes = self.get_boxes(hocr_page_html)
        return bboxes