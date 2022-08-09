import re
from enum import Enum
from pathlib import Path

import datetime
from datetime import timezone
from bs4 import BeautifulSoup

from openpecha.core.annotation import Page, Span
from openpecha.core.annotations import BaseAnnotation
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.ids import get_base_id
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType
from openpecha.core.pecha import OpenPechaFS

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
    

    @property
    def box_height(self):
        y1 = self.vertices[0][1]
        y2 = self.vertices[1][1]
        height = abs(y2-y1)
        return height
    
    @property
    def box_orientation(self):
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

def get_vertices(word_box):
    try:
        vertices_info = word_box['title'].split(';')[0]
    except:
        return []
    vertices_info = vertices_info.replace("bbox ", "")
    vertices_coordinates = vertices_info.split(" ")
    vertices = [
        [vertices_coordinates[0], vertices_coordinates[1]],
        [vertices_coordinates[2], vertices_coordinates[3]]
        ]
    return vertices

def get_confidence(word_box):
    confidence_info = word_box['title']
    confidence = float(re.search("x_wconf (\d+.)", confidence_info).group(1))
    return confidence

def parse_box(word_box):
    vertices = get_vertices(word_box)
    confidence = get_confidence(word_box)
    language = word_box['lang']
    text = word_box.text
    box = BBox(
        text=text,
        vertices=vertices,
        confidence=confidence,
        language=language
    )
    return box


def get_boxes(hocr_html):
    boxes = []
    hocr_html = BeautifulSoup(hocr_html, 'html.parser')
    word_boxes = hocr_html.find_all("span", {"class": "ocrx_word"})
    for word_box in word_boxes:
        boxes.append(parse_box(word_box))
    return boxes


def create_opf(input_dir, output_path):
    boxes = get_boxes(input_dir)
    opf = OpenPechaFS(
        meta= get_metadata(input_dir),
        base=get_base_layer(boxes),
        layers= get_layers(boxes)
        )

    opf.save(output_path=output_path)
    return opf.meta.id