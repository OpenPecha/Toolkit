import json
from pickle import NONE
import tempfile
from pathlib import Path

import py
import pytest   

from openpecha.core.layer import LayerEnum
from openpecha.core.pecha import OpenPechaFS
from openpecha.formatters.ocr import GoogleVisionFormatter
from openpecha.utils import load_yaml, dump_yaml
from test_gv_data_provider import GoogleVisionTestFileProvider

#logging.basicConfig(level=logging.DEBUG)

def test_base_text():
    work_id = "W24767"
    pecha_id = None
    
    ocr_path = Path(__file__).parent / "data" / work_id
    expected_base_text = (Path(__file__).parent / "data" / "opf_expected_datas" / "expected_base_text.txt").read_text(encoding='utf-8')
    buda_data_path = Path(__file__).parent / "data" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "ocr_import_info.yml"
    ocr_import_info = load_yaml(ocr_import_info_path)
    buda_data = load_yaml(buda_data_path)
    image_list_path = Path(__file__).parent / "data"
    data_provider = GoogleVisionTestFileProvider(work_id, image_list_path, buda_data, ocr_import_info, ocr_path)
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = GoogleVisionFormatter(output_path=tmpdirname)
        pecha = formatter.create_opf(data_provider, pecha_id, {}, ocr_import_info)
        base_text = pecha.bases['I3852']
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
    ocr_import_info = load_yaml(ocr_import_info_path)
    buda_data = load_yaml(buda_data_path)
    image_list_path = Path(__file__).parent / "data"
    data_provider = GoogleVisionTestFileProvider(work_id, image_list_path, buda_data, ocr_import_info, ocr_path)

    opf_options = {"ocr_confidence_threshold": 0.9, "max_low_conf_per_page": 50}
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = GoogleVisionFormatter(output_path=tmpdirname)
        pecha = formatter.create_opf(data_provider, pecha_id, opf_options, ocr_import_info)
        pagination_layer = json.loads(pecha.layers['I3852'][LayerEnum.pagination].json(exclude_none=True))
        language_layer = json.loads(pecha.layers['I3852'][LayerEnum.language].json(exclude_none=True))
        confidence_layer = json.loads(pecha.layers['I3852'][LayerEnum.ocr_confidence].json(exclude_none=True))

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
        formatter = GoogleVisionFormatter(output_path=tmpdirname)
        pecha = formatter.create_opf(ocr_path, 1, meta_flag=False)
        assert isinstance(pecha, OpenPechaFS) and pecha.opf_path.is_dir()

if __name__ == "__main__":
    test_base_text()
    test_build_layers()