import tempfile
from pathlib import Path

import pytest
from openpecha import config
from openpecha.utils import load_yaml
from openpecha.formatters import GoogleOCRFormatter

def mock_get_image_list(bdrc_scan_id, vol_name):
    return load_yaml(Path(__file__).parent / "data" / str(vol_name+"-imgseqnum.json"))

def test_google_ocr_base_meta():
    work_id = "W24767"
    pecha_id = "I123456"
    
    ocr_path = Path(__file__).parent / "data" / work_id
    expected_meta_path = Path(__file__).parent / "data" / "expected_google_ocr_meta.yml"
    buda_data_path = Path(__file__).parent / "data" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "ocr_import_info.yml"
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        buda_data = load_yaml(buda_data_path)
        ocr_import_info = load_yaml(ocr_import_info_path)
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        formatter._get_image_list = mock_get_image_list
        pecha_path = formatter.create_opf(ocr_path, pecha_id, ocr_import_info, buda_data)
        output_metadata = load_yaml(Path(f"{pecha_path}/{pecha_path.name}.opf/meta.yml"))
        expected_metadata = load_yaml(expected_meta_path)
        assert output_metadata["source_metadata"] == expected_metadata["source_metadata"]
        del output_metadata["ocr_import_info"]["ocr_info"]
        del expected_metadata["ocr_import_info"]["ocr_info"]
        assert output_metadata["ocr_import_info"] == expected_metadata["ocr_import_info"]
        assert output_metadata["statistics"] == expected_metadata["statistics"]
        assert output_metadata["default_language"] == expected_metadata["default_language"]

if __name__ == "__main__":
    test_google_ocr_base_meta()