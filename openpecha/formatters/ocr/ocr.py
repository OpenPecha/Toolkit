import re
import statistics
import logging

import datetime
from datetime import timezone
from fontTools import unicodedata
from abc import abstractmethod

from openpecha.core.annotation import Page, Span
from openpecha.core.annotations import Language, OCRConfidence
from openpecha.core.layer import Layer, LayerEnum, OCRConfidenceLayer
from openpecha.core.metadata import InitialPechaMetadata, InitialCreationType, LicenseType, Copyright_copyrighted, Copyright_unknown, Copyright_public_domain
from openpecha.core.pecha import OpenPechaFS
from openpecha.formatters import BaseFormatter
from openpecha import __version__

ANNOTATION_MINIMAL_LEN = 20
ANNOTATION_MINIMAL_CONFIDENCE = 0.8
ANNOTATION_MAX_LOW_CONF_PER_PAGE = 10
NO_SPACE_AFTER_PATTERN = re.compile(r"(?:\s|[༌་])$")
# mapping between script tags detected from the text and language recorded
# in the Language layer
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
NO_LANG = ""
UNKNOWN_LANG = "und"
# Unicode character categories taken into account when computing width:
UNICODE_CHARCAT_FOR_WIDTH = ["Ll", "Lu", "Lo", "Nd", "No", "Nl", "Lt"]
UNICODE_CHARCAT_NOT_NOISE = ["Ll", "Lu", "Lo", "Nd", "No", "Nl", "Lt"]
SAME_LINE_RATIO_THRESHOLD = 0.2

class BBox:
    def __init__(self, x1: int, x2: int, y1: int, y2: int, angle: int = None, text: str = None, confidence: float = None, language: str = NO_LANG):
        self.text = text
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.angle = angle
        self.confidence = confidence
        self.language = language
        self.mid_y = (y1 + y2) / 2
        self.mid_x = (x1 + x2) / 2
    
    def get_height(self):
        return self.y2 - self.y1

    def get_width(self):
        return self.x2 - self.x1
    
    def get_angle(self):
        """
        Returns the angle of the BBox. The value is either None (when no angle can be determined)
        or the value of the clockwise rotation, in positive degrees (the value must be between 0 and 359).
        A value of 0 represents straight characters.
        """
        return self.angle

    def get_box_orientation(self):
        width = self.x2 - self.x1
        length = self.y2 - self.y1
        if width > length:
            return "landscape"
        else:
            return "portrait"

    def get_y_mid(self):
        return self.mid_y

    def get_centriod(self):
        return [self.mid_x, self.mid_y]

    def to_debug_str(self):
        return "'%s' [%d,%d,%d,%d]" % (self.text, self.x1, self.x2, self.y1, self.y2)


class OCRFileProvider():
    def __init__(self, ocr_import_info: str):
        self.ocr_import_info = ocr_import_info

    def get_image_list(self, image_group_id: str):
        # to be implemented by sub classes
        # must return a simple list of image ids
        pass

    def get_source_info(self):
        # to be implemented by sub classes
        # must return an dict in the same format as buda.get_buda_scan_info
        pass

    def get_image_data(self, image_group_id, image_id):
        # to be implemented by sub classes
        # must return a list of BBox
        pass

class OCRFormatter(BaseFormatter):
    """
    General OpenPecha Formatter for OCR, must 
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
        self.remove_rotated_boxes = True
        self.remove_duplicate_symbols = True
        self.script_to_lang_map = DEFAULT_SCRIPT_TO_LANG_MAPPING
        self.max_low_conf_per_page = ANNOTATION_MAX_LOW_CONF_PER_PAGE

    def text_preprocess(self, text):
        return text


    def get_avg_bbox_height(self, bboxes):
        """Calculate the average height of bounding bboxs in page

        Args:
            bboxes (list): list of boundingbboxs

        Returns:
            float: average height of bounding ploys
        """
        height_sum = 0
        bboxeswidth = 0
        for bbox in bboxes:
            # weigh by number of characters
            bboxwidth = bbox.get_width()
            bboxeswidth += bboxwidth
            height_sum += bbox.get_height()*bboxwidth
        avg_height = height_sum / bboxeswidth
        logging.debug("average bbox height: %f (%d, %d)", avg_height, height_sum, bboxeswidth)
        return avg_height

    def is_on_same_line(self, prev_bbox, bbox, y_diff_threshold):
        """Check if bounding bbox is in same line as previous bounding bbox
        a threshold to check the conditions set to 10 but it can varies for pecha to pecha

        Args:
            prev_bbox (dict): previous bounding bbox
            bbox (dict): current bounding bbox
            avg_height (float): average height of all the bounding bboxs in page

        Returns:
            boolean: true if bouding bbox is in same line as previous bounding bbox else false
        """
        return (bbox.mid_y - prev_bbox.mid_y) < y_diff_threshold

    def get_bbox_lines(self, bboxes):
        """Return list of lines in page using bounding bboxs of page

        Args:
            bboxes (list): list of all the bounding bboxs

        Returns:
            list: list of lines in page
        """
        lines = []
        cur_line_bboxs = []
        prev_bbox = bboxes[0]
        avg_line_height = self.get_avg_bbox_height(bboxes)
        y_diff_threshold = int(avg_line_height * self.same_line_ratio_threshold)
        for bbox in bboxes:
            if self.is_on_same_line(prev_bbox, bbox, y_diff_threshold):
                cur_line_bboxs.append(bbox)
            else:
                lines.append(cur_line_bboxs)
                cur_line_bboxs  = []
                cur_line_bboxs.append(bbox)
            prev_bbox = bbox
        if cur_line_bboxs:
            lines.append(cur_line_bboxs)
        return lines


    def get_bbox_sorted_on_y(self, bbox_centriods):
        """Sort bounding bboxs centriod base on y coordinates

        Args:
            bbox_centriods (list): list of centriod coordinates

        Returns:
            list: list centriod coordinated sorted base on y coordinate
        """
        bboxes_sorted_on_y = sorted(bbox_centriods , key=lambda k: [k[1]])
        return bboxes_sorted_on_y
    
    def sort_line_and_remove_duplicates(self, line, bboxes):
        """it sorted the curr line using x centriod and
        use that sorted list of centriod, use the centrod co-ordinates
        to get the bboxes object to get the area of the box and 
        remove it if the area overlap or intersection over union percentage.

        Args:
            line (list): list of centriod co-ordinates
            bboxes (dict): dict of bbox object with centriod co-ordinates as key

        Returns:
            list: sorted new line with removed overlaps or duplicates
        """
        sorted_line = sorted(line, key=lambda k: [k[0]])
        if not self.remove_duplicate_symbols:
            return sorted_line
        new_line = []
        prev_x2 = -1
        orig_str = ""
        for i, bbox in enumerate(sorted_line):
            curr_bbox = bboxes[f"{bbox[0]},{bbox[1]}"]
            if curr_bbox.x1 <= prev_x2:
                # check if there is overlap with a previous box on this line:
                duplicate = False
                for j in reversed(range(0, i)):
                    bbox_j = bboxes[f"{sorted_line[j][0]},{sorted_line[j][1]}"]
                    if curr_bbox.x1 > bbox_j.x2:
                        continue
                    if curr_bbox.x2 < bbox_j.x1:
                        break
                    overlap = min(bbox_j.x2, curr_bbox.x2) - max(bbox_j.x1, curr_bbox.x1)
                    if overlap > 0.6 * (curr_bbox.x2 - curr_bbox.x1):
                        duplicate = True
                        logging.debug("remove duplicate symbol ", bbox_j.text)
                        break
                if duplicate:
                    continue
                else:
                    new_line.append(bbox)
            else:
                new_line.append(bbox)
            prev_x2 = curr_bbox.x2
        return new_line
                    

    def get_bbox_sorted_on_x(self, bboxes_sorted_on_y, avg_box_height, bboxes):
        """Groups box belonging in same line using average height and sort the grouped boxes base on x coordinates

        Args:
            bboxes_sorted_on_y (list): list of centriod
            avg_box_height (float): average boxes height

        Returns:
            list: list of sorted centriod
        """
        prev_bbox = bboxes_sorted_on_y[0]
        lines = []
        cur_line = []
        sorted_bboxes = []
        for bbox in bboxes_sorted_on_y:
            if abs(bbox[1]-prev_bbox[1]) < avg_box_height/10:
                cur_line.append(bbox)
            else:
                lines.append(cur_line)
                cur_line = []
                cur_line.append(bbox)
            prev_bbox = bbox
        if cur_line:
            lines.append(cur_line)
        for line in lines:
            sorted_line = self.sort_line_and_remove_duplicates(line, bboxes)
            # sorted_line = sorted(line, key=lambda k: [k[0]])
            for bbox in sorted_line:
                sorted_bboxes.append(bbox)
        return sorted_bboxes

    def sort_bboxes(self, main_region_bboxes):
        """Sort the bounding bboxs

        Args:
            main_region_bboxes (list): list of bounding bboxs

        Returns:
            list: sorted bounding bbox list
        """
        bboxes = {}
        bbox_centriods = []
        avg_box_height = self.get_avg_bbox_height(main_region_bboxes)
        for bbox in main_region_bboxes:
            centroid = bbox.get_centriod()
            bboxes[f"{centroid[0]},{centroid[1]}"] = bbox
            bbox_centriods.append(centroid)
        sorted_bboxes = []
        sort_on_y_bboxs = self.get_bbox_sorted_on_y(bbox_centriods)
        sorted_bbox_centriods = self.get_bbox_sorted_on_x(sort_on_y_bboxs, avg_box_height, bboxes)
        for bbox_centriod in sorted_bbox_centriods:
            sorted_bboxes.append(bboxes[f"{bbox_centriod[0]},{bbox_centriod[1]}"])
        return sorted_bboxes

    def has_space_attached(self, symbol):
        # must be overriden if the format has that kind of information
        return False

    def populate_confidence(self, bboxes):
        """Populate confidence of bounding bboxs of pecha level and image group level

        Args:
            bboxes (list): list of bounding bboxs
        """
        for bbox in bboxes:
            self.word_confidences.append(float(bbox.confidence))
            self.cur_base_word_confidences.append(float(bbox.confidence))

    def bbox_can_have_space_after(self, bbox):
        if NO_SPACE_AFTER_PATTERN.search(bbox.text):
            return False
        return True
        
    def has_space_after(self, cur_bbox, next_bbox, avg_char_width):
        """Checks if there is space between two bbox or not if yes returns a space bbox bbox object

        Args:
            cur_bbox (bbox): first bbox
            next_bbox (bbox): second bbox
            avg_char_width (float): avg width of char in page

        Returns:
            bbox or none: space bbox object
        """
        if next_bbox.x1 - cur_bbox.x2 > avg_char_width*0.75 and self.bbox_can_have_space_after(cur_bbox):
            space_box = BBox(
                cur_bbox.x2,
                next_bbox.x1,
                cur_bbox.y1, # the y coordinates are kind of arbitrary
                cur_bbox.y2,
                angle=0,
                text=" ",
                confidence=None,
                language=None
            )
            return space_box
        return None
    
    def insert_space_bbox(self, bboxes, avg_char_width):
        """Inserts space bounding bbox if missing

        Args:
            bboxes (list): list of bbox objects
            avg_char_width (float): avg width of char

        Returns:
            list: list of bbox objects
        """
        new_bboxes = []
        for bbox_walker, cur_bbox in enumerate(bboxes):
            if bbox_walker == len(bboxes)-1:
                new_bboxes.append(cur_bbox)
            else:
                next_bbox = bboxes[bbox_walker+1]
                space_bbox = self.has_space_after(cur_bbox, next_bbox, avg_char_width)
                if space_bbox:
                    new_bboxes.append(cur_bbox)
                    new_bboxes.append(space_bbox)
                else:
                    new_bboxes.append(cur_bbox)
        return new_bboxes

    def get_main_script_tag(text: str):
        """
        return the ISO 15924 tag of the main script used
        in a string
        """
        halflen = int(len(text) / 2)
        scripts = {}
        maxcharscript_nbchars = 0
        maxcharscript = "Zyyy"
        for i, c in enumerate(text):
            cscript = unicodedata.script(c)
            if cscript not in scripts:
                scripts[cscript] = 0
            script_nbchars = scripts[cscript] + 1
            scripts[cscript] = script_nbchars
            if script_nbchars > maxcharscript_nbchars:
                maxcharscript_nbchars = script_nbchars
                maxcharscript = cscript
            if maxcharscript_nbchars > halflen:
                return maxcharscript
        return maxcharscript


    def get_main_language_code(self, text):
        """returns the language tag for the text

        Args:
            string (str): text from wordbox.text
        """
        main_script = OCRFormatter.get_main_script_tag(text)
        if main_script in self.script_to_lang_map:
            return self.script_to_lang_map[main_script]
        if main_script == "Zyyy" or main_script == "Zxxx":
            return NO_LANG
        return UNKNOWN_LANG

    def is_noise(self, text):
        for c in text:
            if unicodedata.category(c) in UNICODE_CHARCAT_NOT_NOISE:
                return False
        return True

    def add_language(self, bbox, bbox_start_cc, state):
        bbox_lang = bbox.language
        previous_ann = state["latest_language_annotation"]
        bbox_end_cc = state["base_layer_len"] # by construction
        if previous_ann is not None:
            # if bbox has the same language as the latest annotation, we just lengthen the previous
            # annotation to include this bbox:
            if bbox_lang == previous_ann['lang'] or not bbox_lang:
                previous_ann["end"] = bbox_end_cc
                return
            # if bbox is the default language, we just conclude the previous annotation
            if bbox_lang == self.default_language:
                state["latest_language_annotation"] = None
                return
            # else, we create a new annotation
            annotation = {"start": bbox_start_cc, "end": bbox_end_cc, "lang": bbox_lang}
            state["language_annotations"].append(annotation)
            state["latest_language_annotation"] = annotation
            return
        # if there's no previous annotation and language is the default language, return
        if bbox_lang == self.default_language or bbox_lang == NO_LANG or bbox_lang == UNKNOWN_LANG or not bbox_lang:
            return
        # if there's no previous annotation and language is not the default, we create an annotation
        annotation = {"start": bbox_start_cc, "end": bbox_end_cc, "lang": bbox_lang}
        state["language_annotations"].append(annotation)
        state["latest_language_annotation"] = annotation

    def add_low_confidence(self, bbox, bbox_start_cc, state):
        if bbox.confidence is None:
            return
        if bbox.confidence > self.ocr_confidence_threshold:
            state["latest_low_confidence_annotation"] = None
            return
        bbox_end_cc = state["base_layer_len"] # by construction
        if state["latest_low_confidence_annotation"] is not None:
            # average of the confidence indexes, weighted by character length
            state["latest_low_confidence_annotation"]["weights"].append((bbox_end_cc - bbox_start_cc, bbox.confidence))
            state["latest_low_confidence_annotation"]["end"] = bbox_end_cc
        else:
            annotation = {"start": bbox_start_cc, "end": bbox_end_cc, 
                "weights": [(bbox_end_cc - bbox_start_cc, bbox.confidence)]}
            state["page_low_confidence_annotations"].append(annotation)
            state["latest_low_confidence_annotation"] = annotation

    def bbox_line_has_characters(self, bbox_line):
        for bbox in bbox_line:
            if bbox.language != UNKNOWN_LANG and not self.is_noise(bbox.text):
                return True
        if logging.DEBUG >= logging.root.level:
            line = ''
            for bbox in bbox_line:
                line += bbox.text
            logging.debug("ignoring line '%s', detected as noise", line)
        return False

    def build_page(self, bboxes, image_number, image_filename, state, avg_char_width=None):
        sorted_bboxes = self.sort_bboxes(bboxes)
        bbox_lines = self.get_bbox_lines(sorted_bboxes)
        page_start_cc = state["base_layer_len"]
        page_word_confidences = []
        for bbox_line in bbox_lines:
            if self.remove_non_character_lines and not self.bbox_line_has_characters(bbox_line):
                continue
            if avg_char_width:
                bbox_line = self.insert_space_bbox(bbox_line, avg_char_width)
            for bbox in bbox_line:
                state["base_layer"] += bbox.text
                start_cc = state["base_layer_len"]
                state["base_layer_len"] += len(bbox.text)
                if bbox.confidence is not None:
                    state["word_confidences"].append(float(bbox.confidence))
                    page_word_confidences.append(float(bbox.confidence))
                    self.add_low_confidence(bbox, start_cc, state)
                self.add_language(bbox, start_cc, state)
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
                confidence=mean_page_confidence, nb_below_threshold=nb_below_threshold if nb_below_threshold else None)
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

    def confidence_index_from_weighted_list(self, weights):
        sum_weights = 0
        confidence_sum = 0
        for weight, confidence in weights:
            sum_weights += weight
            confidence_sum += weight * confidence
        return confidence_sum / sum_weights

    def merge_page_low_confidence_annotations(self, annotation_list_src, annotations_dst):
        for annotation in annotation_list_src:
            avg_confidence = self.confidence_index_from_weighted_list(annotation["weights"])
            annotation_obj = OCRConfidence(
                span = Span(start=annotation["start"], end=annotation["end"]),
                confidence = avg_confidence)
            annotations_dst[self.get_unique_id()] = annotation_obj

    def merge_short_language_annotations(self, annotation_list):
        annotations = {}
        previous_annotation = None
        # annotation list is in span order
        for annotation in annotation_list:
            if annotation['end'] - annotation['start'] < self.language_annotation_min_len:
                if previous_annotation is not None and annotation['start'] - previous_annotation.span.end < self.language_annotation_min_len:
                    previous_annotation.span.end = annotation['end']
                continue
            if previous_annotation is not None and annotation["lang"] == previous_annotation.language:
                if annotation['start'] - previous_annotation.span.end < self.language_annotation_min_len:
                    previous_annotation.span.end = annotation['end']
                    continue
            previous_annotation = Language(
                span = Span(start=annotation["start"], end=annotation["end"]),
                language = annotation["lang"])
            annotations[self.get_unique_id()] = previous_annotation
        return annotations
    
    @abstractmethod
    def get_bboxes_for_page(self, image_group_id, image_filename):
        # needs to be implemented by inheriting classes
        pass

    def build_base(self, image_group_id):
        """ The main function that takes the OCR results for an entire volume
            and creates its base and layers
        """
        image_list = self.data_provider.get_image_list(image_group_id)
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
        for image_number, image_filename in enumerate(image_list):
            # enumerate starts at 0 but image numbers start at 1
            bboxes, avg_char_width = self.get_bboxes_for_page(image_group_id, image_filename)
            if bboxes:
                self.build_page(bboxes, image_number+1, image_filename, state, avg_char_width)
        layers = {}
        if state["pagination_annotations"]:
            layer = Layer(annotation_type=LayerEnum.pagination, annotations=state["pagination_annotations"])
            layers[LayerEnum.pagination] = layer
        if state["language_annotations"]:
            annotations = self.merge_short_language_annotations(state["language_annotations"])
            layer = Layer(annotation_type=LayerEnum.language, annotations=annotations)
            layers[LayerEnum.language] = layer
        if state["low_confidence_annotations"]:
            layer = OCRConfidenceLayer(
                confidence_threshold=self.ocr_confidence_threshold, 
                annotations=state["low_confidence_annotations"]
            )
            layers[LayerEnum.ocr_confidence] = layer
        return state["base_layer"], layers, state["word_confidences"]

    def get_copyright_and_license_info(self, bdata):
        if "copyright_status" not in bdata["source_metadata"]:
            return {}, None
        cs = bdata["source_metadata"]["copyright_status"]
        if cs == "http://purl.bdrc.io/resource/CopyrightPublicDomain":
            return Copyright_public_domain, LicenseType.CC0
        if cs == "http://purl.bdrc.io/resource/CopyrightUndetermined":
            return Copyright_unknown, None
        return Copyright_copyrighted, LicenseType.UNDER_COPYRIGHT
            
    def get_metadata(self, pecha_id: str = None, ocr_import_info=None) -> InitialPechaMetadata:
        source_metadata = {
            "id": f"http://purl.bdrc.io/resource/{self.bdrc_scan_id}",
            "title": "",
            "author": "",
        }
        copyright = {}
        license = None
        if self.source_info is not None:
            source_metadata = self.source_info["source_metadata"]
            copyright, license = self.get_copyright_and_license_info(self.source_info)

        parser_link = ocr_import_info["parser_link"] if "parser_link" in ocr_import_info else None

        metadata = InitialPechaMetadata(
            id=pecha_id,
            source='https://library.bdrc.io',
            initial_creation_type=InitialCreationType.ocr,
            imported=datetime.datetime.now(timezone.utc),
            last_modified=datetime.datetime.now(timezone.utc),
            parser=parser_link,
            copyright=copyright,
            license=license,
            source_metadata=source_metadata,
            default_language=self.default_language,
            ocr_import_info=ocr_import_info
        )
        return metadata

    def set_base_meta(self, image_group_id, base_file_name, word_confidence_list):
        self.cur_word_confidences = []
        self.base_meta[base_file_name] = {
            "source_metadata": self.source_info["image_groups"][image_group_id],
            "order": self.source_info["image_groups"][image_group_id]["volume_number"],
            "base_file": f"{base_file_name}.txt"
            }
        if word_confidence_list:
            self.base_meta[base_file_name]["statistics"] = {
              "ocr_word_median_confidence_index": statistics.median(word_confidence_list),
              "ocr_word_mean_confidence_index": statistics.mean(word_confidence_list)
            }
    
    def create_opf(self, data_provider, pecha_id=None, opf_options = {}, ocr_import_info = {}):
        """Create opf

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

        self.remove_non_character_lines = opf_options["remove_non_character_lines"] if "remove_non_character_lines" in opf_options else True
        self.remove_rotated_boxes = opf_options["remove_rotated_boxes"] if "remove_rotated_boxes" in opf_options else True
        self.create_language_layer = opf_options["create_language_layer"] if "create_language_layer" in opf_options else True
        self.ocr_confidence_threshold = opf_options["ocr_confidence_threshold"] if "ocr_confidence_threshold" in opf_options else ANNOTATION_MINIMAL_CONFIDENCE
        self.language_annotation_min_len = opf_options["language_annotation_min_len"] if "language_annotation_min_len" in opf_options else ANNOTATION_MINIMAL_LEN
        self.max_low_conf_per_page = opf_options["max_low_conf_per_page"] if "max_low_conf_per_page" in opf_options else ANNOTATION_MAX_LOW_CONF_PER_PAGE
        self.script_to_lang_map = opf_options["script_to_lang_map"] if "script_to_lang_map" in opf_options else DEFAULT_SCRIPT_TO_LANG_MAPPING
        self.same_line_ratio_threshold = opf_options["same_line_ratio_threshold"] if "same_line_ratio_threshold" in opf_options else SAME_LINE_RATIO_THRESHOLD
        self.remove_duplicate_symbols = opf_options["remove_duplicate_symbols"] if "remove_duplicate_symbols" in opf_options else True

        ocr_import_info["op_import_options"] = opf_options
        ocr_import_info["op_import_version"] = __version__
        
        # self._build_dirs(None, id_=pecha_id)

        # if the bdrc scan id is not specified, we assume it's the directory namepecha_id
        self.bdrc_scan_id = self.data_provider.bdrc_scan_id
        self.source_info = self.data_provider.get_source_info()
        self.default_language = "bo" if "expected_default_language" not in ocr_import_info else ocr_import_info["expected_default_language"]
        self.default_language = "bo"
        if "expected_default_language" in ocr_import_info:
            self.default_language = ocr_import_info["expected_default_language"]
        elif "languages" in self.source_info and self.source_info["languages"]:
            self.default_language = self.source_info["languages"][0]

        self.metadata = self.get_metadata(pecha_id, ocr_import_info)
        pecha = OpenPechaFS(metadata=self.metadata)
        total_word_confidence_list = []

        for image_group_id, image_group_info in self.source_info["image_groups"].items():
            base_id = image_group_id
            base_text, layers, word_confidence_list = self.build_base(image_group_id)
            pecha.bases[base_id] = base_text
            pecha.layers[base_id] = layers
            self.set_base_meta(image_group_id, base_id, word_confidence_list)
            total_word_confidence_list += word_confidence_list

        # we add the rest to metadata:
        pecha.meta.bases = self.base_meta
        if total_word_confidence_list:
            pecha.meta.statistics = {
                # there are probably more efficient ways to compute those
                "ocr_word_mean_confidence_index": statistics.mean(total_word_confidence_list),
                "ocr_word_median_confidence_index": statistics.median(total_word_confidence_list)
            }
        pecha.save(output_path=self.output_path)

        return pecha
