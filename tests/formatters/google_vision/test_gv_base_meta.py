import tempfile
import json
from pathlib import Path

import pytest
from openpecha import config
from openpecha.utils import load_yaml, dump_yaml
from openpecha.formatters.ocr.google_vision import GoogleVisionFormatter
from test_gv_data_provider import GoogleVisionTestFileProvider

def mock_get_image_list(bdrc_scan_id, vol_name):
    return load_yaml(Path(__file__).parent / "data" / str(vol_name+"-imgseqnum.json"))

def test_google_ocr_base_meta():
    work_id = "W24767"
    pecha_id = "I123456"
    
    ocr_path = Path(__file__).parent / "data" / work_id
    expected_meta_path = Path(__file__).parent / "data" / "opf_expected_datas" / "expected_google_ocr_meta.yml"
    buda_data_path = Path(__file__).parent / "data" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "ocr_import_info.yml"
    ocr_import_info = load_yaml(ocr_import_info_path)
    buda_data = load_yaml(buda_data_path)
    image_list_path = Path(__file__).parent / "data"
    data_provider = GoogleVisionTestFileProvider(work_id, image_list_path, buda_data, ocr_import_info, ocr_path)
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = GoogleVisionFormatter(output_path=tmpdirname)
        pecha = formatter.create_opf(data_provider, pecha_id, {}, ocr_import_info)
        output_metadata = json.loads(pecha.meta.json(exclude_none=True))
        expected_metadata = load_yaml(expected_meta_path)
        assert output_metadata["source_metadata"] == expected_metadata["source_metadata"]
        del output_metadata["ocr_import_info"]["ocr_info"]["timestamp"]
        del expected_metadata["ocr_import_info"]["ocr_info"]["timestamp"]
        del output_metadata["ocr_import_info"]["op_import_version"]
        del expected_metadata["ocr_import_info"]["op_import_version"]
        assert output_metadata["ocr_import_info"] == expected_metadata["ocr_import_info"]
        assert output_metadata["statistics"] == expected_metadata["statistics"]
        assert output_metadata["default_language"] == expected_metadata["default_language"]
        assert output_metadata["bases"] == expected_metadata["bases"]

if __name__ == "__main__":
    test_google_ocr_base_meta()