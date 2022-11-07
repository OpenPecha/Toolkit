import gzip
import json
import logging
import statistics
from fontTools import unicodedata

from openpecha.formatters.ocr.ocr import OCRFileProvider, OCRFormatter, BBox, UNICODE_CHARCAT_FOR_WIDTH
from openpecha.buda.api import get_buda_scan_info, get_image_list, image_group_to_folder_name

class GoogleVisionBDRCFileProvider(OCRFileProvider):
    def __init__(self, bdrc_scan_id, ocr_import_info, ocr_disk_path=None, mode="local"):
        # ocr_base_path should be the output/ folder in the case of BDRC OCR files
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.mode = mode

    def get_image_list(self, image_group_id):
        buda_il = get_image_list(self.bdrc_scan_id, image_group_id)
        # format should be a list of image_id (/ file names)
        return map(lambda ii: ii["filename"], buda_il)

    def get_source_info(self):
        return get_buda_scan_info(self.bdrc_scan_id)

    def get_image_data(self, image_group_id, image_id):
        # TODO: implement the following modes:
        #  - "s3" (just read images from s3)
        #  - "s3-localcache" (cache s3 files on disk)
        # TODO: handle case where only zip archives are present on s3, one per volume.
        #       This should be indicated in self.ocr_import_info["ocr_info"]
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        expected_ocr_filename = image_id[:image_id.rfind('.')]+".json.gz"
        expected_ocr_path = self.ocr_disk_path / vol_folder / expected_ocr_filename
        ocr_object = None
        try:
            ocr_object = json.load(gzip.open(str(expected_ocr_path), "rb"))
        except:
            logging.exception("could not read "+str(expected_ocr_path))
        return ocr_object

class GoogleVisionFormatter(OCRFormatter):
    """
    OpenPecha Formatter for Google OCR JSON output of scanned pecha.
    """

    def __init__(self, output_path=None, metadata=None):
        super().__init__(output_path, metadata)

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

    def get_language_code_from_gv_poly(self, gv_poly):
        lang = ""
        properties = gv_poly.get("property", {})
        if properties:
            languages = properties.get("detectedLanguages", [])
            if languages:
                lang = languages[0]['languageCode']
        if lang == "" or lang == "und":
            # this is not always true but replacing it with None is worse
            # with our current data
            return self.default_language
        if lang in ["bo", "en", "zh"]:
            return lang
        if lang == "dz":
            return "bo"
        # English is a kind of default for our purpose
        return "en"

    @staticmethod
    def get_bboxinfo_from_vertices(vertices):
        """
        Vertices do not always have dots in the same order. The current hypothesis
        is that their order represents the rotation of characters detected by
        the OCR.

        This is not documented on

        https://cloud.google.com/vision/docs/reference/rest/v1/projects.locations.products.referenceImages#Vertex

        though, so use the angle value with caution.
        """
        if len(vertices) == 0:
            return None
        idx_smallest = -1
        smallest_x = -1
        smallest_y = -1
        largest_x = -1
        largest_y = -1
        for idx, v in enumerate(vertices):
            if "x" not in v or "y" not in v:
                continue
            smallest_x = v["x"] if smallest_x == -1 else min(v["x"], smallest_x)
            smallest_y = v["y"] if smallest_y == -1 else min(v["y"], smallest_y)
            largest_x = max(v["x"], largest_x)
            largest_y = max(v["y"], largest_y)
            # here we have to account for cases where the 4 dots don't form a rectangle
            # because coordinates are shifted by 1, see test_bbox_info for some example
            if abs(v["x"] - smallest_x) < 3 and abs(v["y"] - smallest_y) < 3:
                idx_smallest = idx
        if smallest_x == -1 or smallest_y == -1 or largest_y == -1 or largest_x == -1:
            return None
        angle = None
        if len(vertices) == 4 and idx_smallest != -1:
            angle = 0
            if idx_smallest == 1:
                angle = 270
            if idx_smallest == 2:
                angle = 180
            if idx_smallest == 3:
                angle = 90
        return [smallest_x, largest_x, smallest_y, largest_y, angle]

    def dict_to_bbox(self, word):
        """Convert bounding bbox to BBox object

        Args:
            word (dict): bounding gv_poly of a word infos

        Returns:
            obj: BBox object of bounding bbox
        """
        confidence = word.get('confidence')
        if 'boundingBox' not in word or 'vertices' not in word['boundingBox']:
            return None
        vertices = word['boundingBox']['vertices']
        bboxinfo = GoogleVisionFormatter.get_bboxinfo_from_vertices(vertices)
        if bboxinfo == None:
            return None
        if self.remove_rotated_boxes and bboxinfo[4] > 0:
            return None
        return BBox(bboxinfo[0], bboxinfo[1], bboxinfo[2], bboxinfo[3], bboxinfo[4], 
            confidence=confidence)

    @staticmethod
    def get_width_of_vertices(vertices):
        if len(vertices) < 4:
            return None
        smallest_x = -1
        largest_x = -1
        for v in vertices:
            if "x" not in v or "y" not in v:
                continue
            smallest_x = v["x"] if smallest_x == -1 else min(v["x"], smallest_x)
            largest_x = max(v["x"], largest_x)
        if smallest_x == -1:
            return None
        return largest_x - smallest_x

    def get_char_base_bboxes_and_avg_width(self, response):
        """Return bounding bboxs in page response

        Args:
            response (dict): google ocr output of a page

        Returns:
            list: list of BBox object which saves required info of a bounding bbox
        """
        bboxes = []
        widths = []
        for page in response['fullTextAnnotation']['pages']:
            for block in page['blocks']:
                for paragraph in block['paragraphs']:
                    for word in paragraph['words']:
                        bbox = self.dict_to_bbox(word)
                        if bbox is None:
                            # case where we ignore the bbox for some reason
                            # for instance rotated text
                            continue
                        cur_word = ""
                        for symbol in word['symbols']:
                            symbolunicat = unicodedata.category(symbol['text'][0])
                            if symbolunicat in UNICODE_CHARCAT_FOR_WIDTH:
                                vertices = symbol['boundingBox']['vertices']
                                width = GoogleVisionFormatter.get_width_of_vertices(vertices)
                                if width > 0:
                                    widths.append(width)
                            cur_word += symbol['text']
                            if self.has_space_attached(symbol):
                                cur_word += " "
                        if cur_word:
                            bbox.text = cur_word
                            # the language returned by Google OCR is not particularly helpful
                            # language = self.get_language_code_from_gv_poly(word)
                            # instead we use our custom detection system
                            bbox.language = self.get_main_language_code(cur_word)
                            bboxes.append(bbox)
        avg_width = statistics.mean(widths) if widths else None
        logging.debug("average char width: %f", avg_width)
        return bboxes, avg_width

    def get_bboxes_for_page(self, image_group_id, image_filename):
        ocr_object = self.data_provider.get_image_data(image_group_id, image_filename)
        try:
            page_content = ocr_object["textAnnotations"][0]["description"]
        except Exception:
            logging.error("OCR page is empty (no textAnnotations[0]/description)")
            return None, 0
        return self.get_char_base_bboxes_and_avg_width(ocr_object)
