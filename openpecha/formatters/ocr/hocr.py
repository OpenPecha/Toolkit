from pydoc import pager
import re
import os
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
    def __init__(self, bdrc_scan_id, buda_data, ocr_import_info, ocr_disk_path):
        self.ocr_import_info = ocr_import_info
        # disk path is the path to a directory that contains "info" and "output" subfolders
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.images_info = {}
    

    def get_image_list(self, image_group_id):
        """call get_images_info and return the image_list of the image_group_id

        Args:
            image_group_id (str): image_group_id of the volume
        """
        self.get_images_info(image_group_id)
        buda_il = get_image_list(self.bdrc_scan_id, image_group_id)
        # format should be a list of image_id (/ file names)
        return map(lambda ii: ii["filename"], buda_il)
    
    def get_images_info(self, image_group_id):
        """load page_filename with image_filename mapping to images.info

        Args:
            image_group_id (str): image_group_id of the volume
        """
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        vol_path = Path(f"{self.ocr_disk_path}") / "info" / vol_folder
        if os.path.isdir(vol_path):
            image_info_path = Path(vol_path) / "gb-bdrc-map.json"
            self.images_info = load_yaml(image_info_path)
        else:
            return

    def get_source_info(self):
        return self.buda_data
    
    def get_hocr_filename(self, image_id):
        """ return the filename of the image_id from the images_info dict
        """
        for filename, img_ref in self.images_info.items():
            img_id = img_ref
            if img_id == image_id:
                return filename

    def get_image_data(self, image_group_id, image_filename):
        """get hocr_filename using image_filename,
           use volume folder and hocr_filename to read the hocr_html file for the image_filename or the page

        Args:
            image_group_id (str): image_group_id of the volume

        Returns:
            hocr_html: html file of the image_filename
        """
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        hocr_filename = self.get_hocr_filename(image_filename)
        image_hocr_path = Path(f"{self.ocr_disk_path}") / "output" / vol_folder / f"{hocr_filename}.html"
        if os.path.isfile(image_hocr_path):
            hocr_html = image_hocr_path.read_text(encoding='utf-8')
            return hocr_html
        else:
            return

class HOCRIAFileProvider():
    def __init__(self, bdrc_scan_id, bdrc_image_list_path, buda_data, ocr_import_info, ocr_disk_path=None):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.bdrc_image_list_path = bdrc_image_list_path
        self.images_info = {}


    def get_image_list(self, image_group_id):
        """call get_images_info and return the image_list of the image_group_id

        Args:
            image_group_id (str): image_group_id of the volume
        """
        self.get_images_info(image_group_id)
        buda_il = get_image_list(self.bdrc_scan_id, image_group_id)
        # format should be a list of image_id (/ file names)
        return map(lambda ii: ii["filename"], buda_il)
    
    
    def get_images_info(self, image_group_id):
        """map the image_filename to page_info from the hocr_html and populate the images_info

        Args:
            image_group_id (str): image_group_id of the volume
        """
        curr_image = {}
        image_list = get_image_list(self.bdrc_scan_id, image_group_id)
        image_group_hocr = self.get_image_group_hocr(image_group_id)
        if image_group_hocr :
            hocr_html = BeautifulSoup(image_group_hocr, 'html.parser')
            pages_hocr = hocr_html.find_all("div", {"class": "ocr_page"})
            for image_number, image_filename in enumerate (image_list):
                filename = image_filename['filename']
                for page_hocr in pages_hocr:
                    if int(page_hocr['id'][5:]) == image_number:
                        curr_image[filename] = {
                            'page_info': page_hocr
                        }
                        self.images_info.update(curr_image)
                        curr_image = {}
                
    
    def get_image_group_hocr(self, image_group_id):
        """use volume number and bdrc scan id to read the hocr_html file for the volume

        Args:
            image_group_id (str): image_group_id of the volume

        Returns:
            hocr_html: html file of the volume
        """
        vol_num = self.buda_data['image_groups'][image_group_id]['volume_number']
        image_group_hocr_path = Path(f"{self.bdrc_image_list_path}") / f"bdrc-{self.bdrc_scan_id}-{vol_num}_hocr.html"
        try:
            hocr_html = image_group_hocr_path.read_text(encoding='utf-8')
            return hocr_html
        except:
            return
    
    def get_source_info(self):
        return self.buda_data
        
    
    def get_image_data(self, image_group_id, image_filename):
        """use images_info to return the page_info of the image_filename

        Args:
            image_group_id (str): image_group_id of the volume
        """
        try:
            page_hocr = self.images_info[image_filename]['page_info']
            return page_hocr
        except:
            return
    
class HOCRFormatter(OCRFormatter):
    """
    OpenPecha Formatter for Google OCR HOCR output of scanned pecha.
    """
    def __init__(self, mode=None, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
        self.mode = mode
        self.word_span = 0

    def get_confidence(self, word_box):
        confidence_info = word_box['title']
        confidence = float(int(re.search(r"x_wconf (\d+)", confidence_info).group(1))/100)
        return confidence

    
    def get_word_text_with_space(self, line_text, word_box):
        """check for space after word_text using line_text, add space to word_text if found 
        """
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
        
    def parse_box(self, line_box, word_box):
        """parse the word_box to create bbox for the text in word_box.

       Args:
            line_text (_type_): line from the page html 
            word_box (_type_): word from the above line

        Returns:
            box : bbox for text in word_box with vertices, confidence, language 
        """
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
        language = self.get_main_language_code(word_box.text)
        text = self.get_word_text_with_space(line_text, word_box)
        box = BBox(x1, x2, y1, y2,
            text=text,
            confidence=confidence,
            language=language
        )
        return box
    
    def get_boxes(self, hocr_page_html):
        """parse the hocr_page_html for one html file per page for bboxes of the page

        Args:
            hocr_page_html (html): html of the page

        Returns:
            boxes: list of bbox dict
        """
        bboxes = []
        hocr_html = BeautifulSoup(hocr_page_html, 'html.parser')
        line_boxes = hocr_html.find_all("span", {"class": "ocr_line"})
        for line_box in line_boxes:
            self.word_span = 0
            word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
            for word_box in word_boxes:
                bboxes.append(self.parse_box(line_box,word_box))
        return bboxes
    
    def get_boxes_for_IA(self, page_html):
        """parse the page_html for one html file per volume for bboxes of the page

        Args:
            hocr_page_html (html): html of the page

        Returns:
            boxes: list of bbox dict
        """
        bboxes = []
        paragraphs_html = page_html.find_all("p", {"class": "ocr_par"})
        for paragraph_html in paragraphs_html:
            line_boxes = paragraph_html.find_all("span", {"class": "ocr_line"})
            for line_box in line_boxes:
                self.word_span = 0
                word_boxes = line_box.find_all("span", {"class": "ocrx_word"})
                for word_box in word_boxes:
                    bboxes.append(self.parse_box(line_box, word_box))
        return bboxes


    def get_bboxes_for_page(self, image_group_id, image_filename):
        bboxes = []
        hocr_page_html = self.data_provider.get_image_data(image_group_id, image_filename)
        if hocr_page_html:
            if self.mode == "IA":
                bboxes = self.get_boxes_for_IA(hocr_page_html)
            else:
                bboxes = self.get_boxes(hocr_page_html)
        return bboxes, None

    