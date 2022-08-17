import json
import tempfile
from pathlib import Path

import py
import pytest
from openpecha.formatters import google_ocr

from openpecha.formatters.google_ocr import GoogleOCRFormatter
from openpecha.utils import load_yaml, dump_yaml

def mock_get_image_list(bdrc_scan_id, vol_name):
    return load_yaml(Path(__file__).parent / "data" / str(vol_name+"-imgseqnum.json"))  


def test_base_text():
    work_id = "W24767"
    pecha_id = "I123456"
    
    ocr_path = Path(__file__).parent / "data" / work_id
    expected_base_text = (Path(__file__).parent / "data" / "opf_expected_datas" / "expected_base_text.txt").read_text(encoding='utf-8')
    buda_data_path = Path(__file__).parent / "data" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "ocr_import_info.yml"
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        buda_data = load_yaml(buda_data_path)
        ocr_import_info = load_yaml(ocr_import_info_path)
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        formatter._get_image_list = mock_get_image_list
        pecha_path = formatter.create_opf(ocr_path, pecha_id, ocr_import_info, buda_data)
        base_text = (pecha_path / f"{pecha_path.name}.opf" / "base" / "I3852.txt").read_text(encoding='utf-8')
        assert expected_base_text == base_text

def test_build_layers():
    work_id = "W24767"
    pecha_id = "I123456"
    
    ocr_path = Path(__file__).parent / "data" / work_id
    expected_pagination_layer = load_yaml((Path(__file__).parent / "data" / "opf_expected_datas" / "expected_Pagination.yml"))
    expected_language_layer = load_yaml((Path(__file__).parent / "data" / "opf_expected_datas" / "expected_Language.yml"))
    expected_confidence_layer = load_yaml((Path(__file__).parent / "data" / "opf_expected_datas" / "expected_OCRConfidence.yml"))
    buda_data_path = Path(__file__).parent / "data" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "ocr_import_info.yml"
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        buda_data = load_yaml(buda_data_path)
        ocr_import_info = load_yaml(ocr_import_info_path)
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        formatter._get_image_list = mock_get_image_list
        pecha_path = formatter.create_opf(ocr_path, pecha_id, ocr_import_info, buda_data)
        pagination_layer = load_yaml((pecha_path / f"{pecha_path.name}.opf" / "layers" / "I3852" / "Pagination.yml"))
        language_layer = load_yaml((pecha_path / f"{pecha_path.name}.opf" / "layers" / "I3852" / "Language.yml"))
        confidence_layer = load_yaml((pecha_path / f"{pecha_path.name}.opf" / "layers" / "I3852" / "OCRConfidence.yml"))

        ###Pagination layer testing
        for (_, expected_ann), (_, ann) in zip(expected_pagination_layer['annotations'].items(), pagination_layer['annotations'].items()):
            assert expected_ann == ann
        
        ###Language layer testing
        for (_, expected_ann), (_, ann) in zip(expected_language_layer['annotations'].items(), language_layer['annotations'].items()):
            assert expected_ann == ann
        
        ###Confidence layer testing
        for (_, expected_ann), (_, ann) in zip(expected_confidence_layer['annotations'].items(), confidence_layer['annotations'].items()):
            assert expected_ann == ann


@pytest.mark.skip(reason="bdrc api failing")
def test_with_gzip_json():
    ocr_path = Path(__file__).parent / "data" / "W1PD95844"
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        pecha_path = formatter.create_opf(ocr_path, 1, meta_flag=False)
        assert isinstance(pecha_path, Path) and pecha_path.is_dir()

if __name__ == "__main__":
    test_build_layers()