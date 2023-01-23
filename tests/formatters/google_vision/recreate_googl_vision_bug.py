from pathlib import Path

from openpecha.formatters.ocr.ocr import OCRFormatter
from openpecha.formatters.ocr.google_vision import GoogleVisionFormatter, GoogleVisionBDRCFileProvider
from openpecha.utils import load_yaml


ocr_path = Path(__file__).parent / "data" / "36940497.json"

def test_to_recreate_bug():

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

    ocr_object = load_yaml(ocr_path)
    
    google_formatter = GoogleVisionFormatter()
    
    bboxes, avg_char_width = google_formatter.get_char_base_bboxes_and_avg_width(response=ocr_object)
    
    ocr_formatter = OCRFormatter()
    ocr_formatter.remove_duplicate_symbols = True
    ocr_formatter.same_line_ratio_threshold = 0.2

    ocr_formatter.build_page(bboxes, 1, "36940497", state, avg_char_width)
    base = state['base_layer']


if __name__ == "__main__":
    test_to_recreate_bug()