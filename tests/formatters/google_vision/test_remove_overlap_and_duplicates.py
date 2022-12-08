import re
from pathlib import Path

from openpecha.formatters.ocr.ocr import OCRFormatter
from openpecha.formatters.ocr.google_vision import GoogleVisionFormatter, GoogleVisionBDRCFileProvider
from openpecha.utils import load_yaml


ocr_path = Path(__file__).parent / "data" / "I1PD958780125.json"
expected_output = (Path(__file__).parent / "data" / "expected_output_of_I1PD958780125.txt").read_text(encoding='utf-8')
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

ANNOTATION_MINIMAL_LEN = 20
ANNOTATION_MINIMAL_CONFIDENCE = 0.8
ANNOTATION_MAX_LOW_CONF_PER_PAGE = 10
NO_SPACE_AFTER_PATTERN = re.compile(r"(?:\s|[༌་])$")
DEFAULT_SCRIPT_TO_LANG_MAPPING = {
    "Tibt": "bo",
    "Deva": "sa-Deva",
    "Hani": "zh",
    "Hans": "zh",
    "Hant": "zh",
    "Latn": "en",
    "Mong": "mn-Mong",
    "Newa": "sa-Newa",
    "Soyo": "mn-Soyo"
}

SAME_LINE_RATIO_THRESHOLD = 0.2

def test_remove_overlap_and_duplicates():
    opf_options = {}
    ocr_object = load_yaml(ocr_path)
    
    google_formatter = GoogleVisionFormatter()
    google_formatter.script_to_lang_map = opf_options["script_to_lang_map"] if "script_to_lang_map" in opf_options else DEFAULT_SCRIPT_TO_LANG_MAPPING
    
    bboxes, avg_char_width = google_formatter.get_char_base_bboxes_and_avg_width(response=ocr_object)
    
    ocr_formatter = OCRFormatter()
    ocr_formatter.same_line_ratio_threshold = opf_options["same_line_ratio_threshold"] if "same_line_ratio_threshold" in opf_options else SAME_LINE_RATIO_THRESHOLD
    ocr_formatter.max_low_conf_per_page = opf_options["max_low_conf_per_page"] if "max_low_conf_per_page" in opf_options else ANNOTATION_MAX_LOW_CONF_PER_PAGE

    ocr_formatter.build_page(bboxes, 1, "I1PD958780125", state, avg_char_width)
    base = state['base_layer']

    assert base == expected_output
    

if __name__ == "__main__":
    test_remove_overlap_and_duplicates()