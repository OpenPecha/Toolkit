from openpecha.buda.api import image_group_to_folder_name
from openpecha.utils import load_yaml
from openpecha.formatters.hocr import Hocr_Parser
from pathlib import Path
import logging

class GoogleBooksTestFileProvider():
    def __init__(self, bdrc_scan_id, buda_data, ocr_import_info, ocr_disk_path=None):
        self.ocr_import_info = ocr_import_info
        self.ocr_disk_path = ocr_disk_path
        self.bdrc_scan_id = bdrc_scan_id
        self.buda_data = buda_data
        self.image_info = {}


    def get_image_list(self, image_group_id):
        bdrc_image_list = load_yaml(self.bdrc_image_list_path / str(image_group_id+".json"))
        return map(lambda ii: ii["filename"], bdrc_image_list)


    def get_source_info(self):
        return self.buda_data


    def get_hocr_filename(self, image_id, image_group_id):
        for filename, img_ref in self.images_info.items():
            img_id = img_ref[:-4]
            if img_id == image_id:
                return filename
    
    
    def get_image_bounding_polys(self, image_group_id, image_id):
        vol_folder = image_group_to_folder_name(self.bdrc_scan_id, image_group_id)
        hocr_filename = self.get_hocr_filename(image_id, image_group_id)
        image_hocr_path = Path(f"{self.ocr_disk_path}/google_books/batch_2022/output/{vol_folder}/{hocr_filename}.html")
        bounding_polys = None
        try:
            parser = Hocr_Parser()
            bounding_polys = parser.parse_hocr(image_hocr_path)
        except Exception as e:
            logging.exception("could not read "+str(image_hocr_path))
            print(e)
        return bounding_polys